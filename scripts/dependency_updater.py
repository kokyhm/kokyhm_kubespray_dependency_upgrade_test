import os
import re
import sys
import logging
import requests
import time
import json
import argparse
import hashlib
from ruamel.yaml import YAML
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from concurrent.futures import ThreadPoolExecutor
from dependency_config import component_info, architectures, oses, path_download, path_checksum, path_main, path_readme, path_version_diff


yaml = YAML()
yaml.explicit_start = True
yaml.preserve_quotes = True
yaml.width = 4096
yaml.indent(mapping=2, sequence=4, offset=2)


pwd = os.getcwd()
cache_dir = './cache'
cache_expiry_seconds = 86400
os.makedirs(cache_dir, exist_ok=True)


github_api_url = 'https://api.github.com/graphql'
gh_token = os.getenv('GH_TOKEN')
if not gh_token:
    logging.error('GH_TOKEN is not set. You can set it via "export GH_TOKEN=<your-token>". Exiting.')
    sys.exit(1)


def setup_logging(loglevel):
    log_format = '%(asctime)s - %(levelname)s - [%(threadName)s] - %(message)s'
    numeric_level = getattr(logging, loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {loglevel}')
    logging.basicConfig(level=numeric_level, format=log_format)

def get_session_with_retries():
    session = requests.Session()
    adapter = HTTPAdapter(
        pool_connections=50,
        pool_maxsize=50,
        max_retries=Retry(total=3, backoff_factor=1)
    )
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def get_current_version(component, component_data):
    kube_major_version = component_data['kube_major_version']
    placeholder_version = [kube_major_version if item == 'kube_major_version' else item for item in component_data['placeholder_version']]
    if component.startswith('kube'):
        current_version = main_yaml_data
    else:
        current_version = download_yaml_data
    for key in placeholder_version:
        current_version = current_version.get(key)
    return current_version

def get_latest_version(component, repo_metadata):
    component_metadata = repo_metadata.get(component)
    releases = component_metadata.get('releases', {}).get('nodes', [])
    for release in releases:
        if release.get('isLatest', False):
            logging.debug(f"Component {component} latest version: {release['tagName']}")
            return release['tagName']
    
    tags = component_metadata.get('refs', {}).get('nodes', [])
    if tags:
        first_tag = tags[0]['name']
        logging.debug(f"Component {component} latest version: {first_tag}")
        return first_tag

    logging.error(f"Component {component} latest version: No releases or tags found.")
    return None

def get_repository_metadata(component_info, session):
    query_parts = []
    for component, data in component_info.items():
        owner = data['owner']
        repo = data['repo']
        query_parts.append(f"""
            {component}: repository(owner: "{owner}", name: "{repo}") {{
                releases(first: {args.graphql_number_of_entries}, orderBy: {{field: CREATED_AT, direction: DESC}}) {{
                    nodes {{
                        tagName
                        url
                        description
                        publishedAt
                        isLatest
                    }}
                }}
                refs(refPrefix: "refs/tags/", first: {args.graphql_number_of_entries}, orderBy: {{field: TAG_COMMIT_DATE, direction: DESC}}) {{
                    nodes {{
                        name
                        target {{
                            ... on Tag {{
                                target {{
                                    ... on Commit {{
                                        history(first: {args.graphql_number_of_commits}) {{
                                            edges {{
                                                node {{
                                                    oid
                                                    message
                                                    url
                                                }}
                                            }}
                                        }}
                                    }}
                                }}
                            }}
                            ... on Commit {{
                                # In case the tag directly points to a commit
                                history(first: {args.graphql_number_of_commits}) {{
                                    edges {{
                                        node {{
                                            oid
                                            message
                                            url
                                        }}
                                    }}
                                }}
                            }}
                        }}
                    }}
                }}
            }}
        """)    
    
    query = f"query {{ {''.join(query_parts)} }}"
    headers = {
        'Authorization': f'Bearer {gh_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = session.post(github_api_url, json={'query': query}, headers=headers)
        response.raise_for_status()
        json_data = response.json()
        data = json_data.get('data')
        if data is not None and bool(data):  # Ensure 'data' is not None and not empty
            logging.debug(f"GraphQL data response:\n{json.dumps(data, indent=2)}")
            return data
        else:
            logging.error(f"GraphQL query returned errors: {json_data}")
            return None
    except Exception as e:
        logging.error(f'Error fetching repository metadata: {e}')
        return None

def calculate_checksum(cachefile, arch, url_download):
    if url_download.endswith('.sha256sum'):
        with open(f'cache/{cachefile}', 'r') as f:
            checksum_line = f.readline().strip()
            return checksum_line.split()[0]
    elif url_download.endswith('SHA256SUMS'):
        with open(f'cache/{cachefile}', 'r') as f:
            for line in f:
                if 'linux' in line and arch in line:
                    return line.split()[0]
    elif url_download.endswith('bsd'):
        with open(f'cache/{cachefile}', 'r') as f:
            for line in f:
                if 'SHA256' in line and 'linux' in line and arch in line:
                    return line.split()[0]
    sha256_hash = hashlib.sha256()
    with open(f'cache/{cachefile}', 'rb') as f:
        for byte_block in iter(lambda: f.read(4096), b''):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def download_file_and_get_checksum(component, arch, url_download, session):
    cache_file = f'{component}-{arch}'
    if os.path.exists(f'cache/{cache_file}'):
        logging.info(f'Using cached file for {url_download}')
        return calculate_checksum(cache_file, arch, url_download)
    try:
        response = session.get(url_download, timeout=10)
        response.raise_for_status()
        with open(f'cache/{cache_file}', 'wb') as f:
            f.write(response.content)
        logging.info(f'Downloaded and cached file for {url_download}')
        return calculate_checksum(cache_file, arch, url_download)
    except Exception as e:
        logging.error(e)
        return None

def get_checksums(component, component_data, version, session):
    checksums = {}
    url_download_template = component_data['url_download'].replace('VERSION', version)
    if component_data['checksum_structure'] == 'os_arch':
        # OS -> Arch -> Checksum
        for os_name in oses:
            checksums[os_name] = {}
            for arch in architectures:
                url_download = url_download_template.replace('OS', os_name).replace('ARCH', arch)
                checksum = download_file_and_get_checksum(component, arch, url_download, session)
                if not checksum:
                    checksum = 0
                checksums[os_name][arch] = checksum
    elif component_data['checksum_structure'] == 'arch':
        # Arch -> Checksum
        for arch in architectures:
            url_download = url_download_template.replace('ARCH', arch)
            checksum = download_file_and_get_checksum(component, arch, url_download, session)
            if not checksum:
                checksum = 0
            checksums[arch] = checksum
    elif component_data['checksum_structure'] == 'simple':
        # Checksum
        checksum = download_file_and_get_checksum(component, '', url_download_template, session)
        if not checksum:
            checksum = 0
        checksums[version] = checksum
    return checksums

def update_yaml_checksum(component_data, checksums, version):
    placeholder_checksum = component_data['placeholder_checksum']
    checksum_structure = component_data['checksum_structure']
    current = checksum_yaml_data[placeholder_checksum]
    if checksum_structure == 'simple': 
        # Simple structure (placeholder_checksum -> version -> checksum)
        current[(version)] = checksums[version]
    elif checksum_structure == 'os_arch':  
        # OS structure (placeholder_checksum -> os -> arch -> version -> checksum)
        for os_name, arch_dict in checksums.items():
            os_current = current.setdefault(os_name, {})
            for arch, checksum in arch_dict.items():
                os_current[arch] = {(version): checksum, **os_current.get(arch, {})}
    elif checksum_structure == 'arch':
        # Arch structure (placeholder_checksum -> arch -> version -> checksum)
        for arch, checksum in checksums.items():
            current[arch] = {(version): checksum, **current.get(arch, {})}
    logging.info(f'Updated {placeholder_checksum} with {checksums}')

def resolve_kube_dependent_component_version(component, component_data, version):
    kube_major_version = component_data['kube_major_version']
    if component in ['crictl', 'crio']:
        try:
            component_major_minor_version = get_major_minor_version(version)
            if component_major_minor_version == kube_major_version:
                resolved_version = kube_major_version
            else:
                resolved_version = component_major_minor_version
        except (IndexError, AttributeError):
            logging.error(f'Error parsing version for {component}: {version}')
            return
    else:
        resolved_version = kube_major_version
    return resolved_version

def update_yaml_version(component, component_data, version):
    placeholder_version = component_data['placeholder_version']
    resolved_version = resolve_kube_dependent_component_version(component, component_data, version)
    updated_placeholder = [
        resolved_version if item == 'kube_major_version' else item 
        for item in placeholder_version
    ]
    current = download_yaml_data
    if len(updated_placeholder) == 1:
        current[updated_placeholder[0]] = version
    else:
        for key in updated_placeholder[:-1]:
            current = current.setdefault(key, {})
        final_key = updated_placeholder[-1]
        if final_key in current:
            current[final_key] = version
        else:
            new_entry = {final_key: version, **current}
            current.clear()
            current.update(new_entry)
    logging.info(f'Updated {updated_placeholder} to {version}')

def update_readme(component, version):
    for i, line in enumerate(readme_data):
        if component in line and re.search(r'v\d+\.\d+\.\d+', line):
            readme_data[i] = re.sub(r'v\d+\.\d+\.\d+', version, line)
            logging.info(f"Updated {component} to {version} in README")
            break
    return readme_data

def create_json_file(file_path):
    new_data = {}
    try:
        with open(file_path, 'w') as f:
            json.dump(new_data, f, indent=2)
        return new_data
    except Exception as e:
        logging.error(f'Failed to create {file_path}: {e}')
        return None

def save_json_file(file_path, data):
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        logging.error(f'Failed to save {file_path}: {e}')
        return False

def load_yaml_file(yaml_file):
    try:
        with open(yaml_file, 'r') as f:
            return yaml.load(f)
    except Exception as e:
        logging.error(f'Failed to load {yaml_file}: {e}')
        return {}

def save_yaml_file(yaml_file, data):
    try:
        with open(yaml_file, 'w') as f:
            yaml.dump(data, f)
    except Exception as e:
        logging.error(f'Failed to save {yaml_file}: {e}')
        return False
    
def open_readme(path_readme):
    try:
        with open(path_readme, 'r') as f:
            return f.readlines()
    except Exception as e:
        logging.error(f'Failed to load {path_readme}: {e}')
        return False

def save_readme(path_readme):
    try:
        with open(path_readme, 'w') as f:
            f.writelines(readme_data)
    except Exception as e:
        logging.error(f'Failed to save {path_readme}: {e}')
        return False
    
def process_version_string(component, version):
    if component in ['youki', 'nerdctl', 'cri_dockerd', 'containerd']:
        if version.startswith('v'):
            version = version[1:]
            return version
    match = re.search(r'release-(\d{8})', version) # gvisor
    if match:
        version = match.group(1)
    return version

def get_major_minor_version(version):
    match = re.match(r'^(v\d+)\.(\d+)', version)
    if match:
        return f"{match.group(1)}.{match.group(2)}"
    return version

def process_component(component, component_data, repo_metadata, session):
    logging.info(f'Processing component: {component}')

    # Get current kube version
    kube_version = main_yaml_data.get('kube_version')
    kube_major_version = get_major_minor_version(kube_version)
    component_data['kube_version'] = kube_version  # needed for nested components
    component_data['kube_major_version'] = kube_major_version  # needed for nested components

    # Get current component version
    current_version = get_current_version(component, component_data)
    if not current_version:
        logging.info(f'Stop processing component {component}, current version unknown')
        return

    # Get latest component version
    latest_version = get_latest_version(component, repo_metadata)
    if not latest_version:
        logging.info(f'Stop processing component {component}, latest version unknown.')
        return
    
    # Basic logging
    if current_version == latest_version:
        logging.info(f'Component {component}, version {current_version} is up to date')
    else:
        logging.info(f'Component {component} version discrepancy, current={current_version}, latest={latest_version}')

    # CI - write data and return
    if args.ci_check:
        version_diff[component] = {
            # used in dependecy-check.yml workflow
            'current_version' : current_version,
            'latest_version' : latest_version,
            # used in generate_pr_body.py script
            'owner' : component_data['owner'],
            'repo' : component_data['repo'],
            'repo_metadata' : repo_metadata,
        }
        return
    
    # Handle skip_checksum script argument
    if args.skip_checksum:
        logging.info(f'Stop processing component {component} due to script argument.')
        return
    
    # Process version string, remove v, etc.
    latest_version = process_version_string(component, latest_version)
    
    # Get checksums
    checksums = get_checksums(component, component_data, latest_version, session)
    # Update checksums
    update_yaml_checksum(component_data, checksums, latest_version)

    # Update version in configuration
    if component not in ['kubeadm', 'kubectl', 'kubelet']: # kubernetes dependent components
        update_yaml_version(component, component_data, latest_version)

    # Update version in README
    if component in ['etcd', 'containerd', 'crio', 'calicoctl', 'krew', 'helm']: # in README
        if component in ['crio', 'crictl']:
            component_major_minor_version = get_major_minor_version(latest_version)
            if component_major_minor_version != kube_major_version: # do not update README, we just added checksums
                return
            component = component.replace('crio', 'cri-o')
        elif component == 'containerd':
            latest_version = f'v{latest_version}'
        elif component == 'calicoctl':
            component = component.replace('calicoctl', 'calico')
        update_readme(component, latest_version)

def main():
    # Setup logging
    setup_logging(args.loglevel)
    # Setup session with retries
    session = get_session_with_retries()

    # Load configuration files
    global main_yaml_data, checksum_yaml_data, download_yaml_data, readme_data, version_diff
    main_yaml_data = load_yaml_file(path_main)
    checksum_yaml_data = load_yaml_file(path_checksum)
    download_yaml_data = load_yaml_file(path_download)
    readme_data = open_readme(path_readme)
    if not (main_yaml_data and checksum_yaml_data and download_yaml_data and readme_data):
        logging.error(f'Failed to open one or more configuration files, current working directory is {pwd}. Exiting...')
        sys.exit(1)

    # CI -create JSON file for version discrepancies
    if args.ci_check:
        version_diff = create_json_file(path_version_diff)
        if version_diff is None:
            logging.error(f'Failed to create version_diff.json file')
            sys.exit(1)

    # Process single component
    if args.component != 'all':
        if args.component in component_info:
            specific_component_info = {args.component: component_info[args.component]}
            # Get repository metadata => releases, tags and commits
            repo_metadata = get_repository_metadata(specific_component_info, session)
            if not repo_metadata:
                sys.exit(1)
            process_component(args.component, component_info[args.component], repo_metadata, session)
        else:
            logging.error(f'Component {args.component} not found in config.')
            sys.exit(1)
    # Process all components in the configuration file concurrently
    else:
        # Get repository metadata => releases, tags and commits
        repo_metadata = get_repository_metadata(component_info, session)
        if not repo_metadata:
            sys.exit(1)
        with ThreadPoolExecutor(max_workers=args.max_workers) as executor:
            futures = []
            logging.info(f'Running with {executor._max_workers} executors')
            for component, component_data in component_info.items():
                futures.append(executor.submit(process_component, component, component_data, repo_metadata, session))
            for future in futures:
                future.result()        

    # CI - save JSON file
    if args.ci_check:
        save_json_file(path_version_diff, version_diff)
    # Save configurations
    else:
        save_yaml_file(path_checksum, checksum_yaml_data)
        save_yaml_file(path_download, download_yaml_data)
        save_readme(path_readme)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Kubespray version and checksum updater for dependencies')
    parser.add_argument('--loglevel', default='INFO', help='Set the log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)')
    parser.add_argument('--component', default='all', help='Specify a component to process, default is all components')
    parser.add_argument('--max-workers', type=int, default=4, help='Maximum number of concurrent workers, use with caution(sometimes less is more)')
    parser.add_argument('--skip-checksum', action='store_true', help='Skip checksum if the current version is up to date')
    parser.add_argument('--ci-check', action='store_true', help='Check versions, store discrepancies in version_diff.json')
    parser.add_argument('--graphql-number-of-entries', type=int, default=10, help='Number of releases/tags to retrieve from Github GraphQL per component (default: 10)')
    parser.add_argument('--graphql-number-of-commits', type=int, default=5, help='Number of commits to retrieve from Github GraphQL per tag (default: 5)')
    args = parser.parse_args()

    main()