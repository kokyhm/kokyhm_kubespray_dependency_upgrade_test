import os
import re
import logging
import requests
import time
import json
import argparse
import requests
import hashlib
from ruamel.yaml import YAML
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from concurrent.futures import ThreadPoolExecutor
from config import component_info, architectures, oses, path_download, path_checksum, path_main

yaml = YAML()
yaml.explicit_start = True
yaml.preserve_quotes = True
yaml.width = 4096
yaml.indent(mapping=2, sequence=4, offset=2)

main_yaml_data = {}
checksum_yaml_data = {}
download_yaml_data = {}

cache_dir = './cache'
cache_expiry_seconds = 86400
os.makedirs(cache_dir, exist_ok=True)

def setup_logging(loglevel):
    numeric_level = getattr(logging, loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {loglevel}')
    logging.basicConfig(level=numeric_level, format='%(asctime)s - %(levelname)s - %(message)s')

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

def load_from_cache(component):
    cache_file = os.path.join(cache_dir, f'{component}.json')
    if os.path.exists(cache_file):
        file_age = time.time() - os.path.getmtime(cache_file)
        if file_age < cache_expiry_seconds:
            logging.info(f'Using cached release info for {component}')
            with open(cache_file, 'r') as f:
                return json.load(f)
    return None

def save_to_cache(component, data):
    os.makedirs(cache_dir, exist_ok=True)
    cache_file = os.path.join(cache_dir, f'{component}.json')
    with open(cache_file, 'w') as f:
        json.dump(data, f, indent=2)
    logging.info(f'Cached release info for {component}')

def get_current_version(component_data):
    kube_major_version = component_data['kube_major_version']
    placeholder_version = [kube_major_version if item == 'kube_major_version' else item for item in component_data['placeholder_version']]

    current_version = download_yaml_data
    for key in placeholder_version:
        current_version = current_version.get(key)

    return current_version

def get_latest_version(component, component_data, session):
    release_info = load_from_cache(component)
    if not release_info:    
        try:
            response = session.get(component_data['url_release'], timeout=10)
            response.raise_for_status()
            release_info = response.json()
            save_to_cache(component, release_info)
        except json.JSONDecodeError: # handle kube* components returning version as a string
            release_info = {'tag_name': response.text}
        except Exception as e:
            logging.error(f'Error fetching latest version for {component}: {e}')
            return None
    latest_version = None
    try:
        # Generic
        if isinstance(release_info, dict):
            latest_version = release_info.get('tag_name', None)
        # Gvisor
        elif isinstance(release_info, list):
            latest_version = release_info[0]['name']
    except:
        latest_version = None

    # Extract version for Gvisor
    if isinstance(latest_version, str) and component in ['gvisor_containerd_shim', 'gvisor_runsc']:
        latest_version = re.sub(r'^release-([0-9]+).*', r'\1', latest_version)

    # Strip v for specific components
    if isinstance(latest_version, str) and component in ['youki', 'nerdctl', 'cri_dockerd', 'containerd']:
        latest_version = latest_version.lstrip('v')

    return latest_version

def calculate_checksum(cachefile, url_download, arch):
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
    with open(f'cache/{cachefile}', "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
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
    logging.info(f'Updating {placeholder_checksum} with {checksums}')
    
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

def resolve_kube_dependent_component_version(component, component_data, version):
    kube_major_version = component_data['kube_major_version']
    if component in ['crictl', 'crio']:
        try:
            component_major_version = '.'.join(version.split('.')[:2])
            if component_major_version == kube_major_version:
                resolved_version = kube_major_version
            else:
                resolved_version = component_major_version
        except (IndexError, AttributeError):
            logging.error(f"Error parsing version for {component}: {version}")
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
    logging.info(f'Updating {updated_placeholder} to {version}')
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

def load_yaml_file(yaml_file):
    try:
        with open(yaml_file, 'r') as f:
            return yaml.load(f)
    except FileNotFoundError:
        logging.warning(f'YAML file {yaml_file} not found.')
        return {}

def save_yaml_file(yaml_file, data):
    with open(yaml_file, 'w') as f:
        yaml.dump(data, f)

def process_component(component, component_data, session):
    logging.info(f'Processing component: {component}')

    kube_version = main_yaml_data.get('kube_version')
    kube_major_version = '.'.join(kube_version.split('.')[:2])
    component_data['kube_major_version'] = kube_major_version # needed for the update of nested versions

    current_version = get_current_version(component_data)
    latest_version = get_latest_version(component, component_data, session)

    if args.skip_if_up_to_date and current_version == latest_version:
        logging.info(f'Skipping component {component}: current version {current_version} is up-to-date.')
        return
    
    if latest_version and not component.startswith("kube"):
        update_yaml_version(component, component_data, latest_version)
        checksums = get_checksums(component, component_data, latest_version, session)
        update_yaml_checksum(component_data, checksums, latest_version)

def main(loglevel, maxworkers, component):
    setup_logging(loglevel)
    
    session = get_session_with_retries()

    global main_yaml_data, checksum_yaml_data, download_yaml_data
    main_yaml_data = load_yaml_file(path_main)
    checksum_yaml_data = load_yaml_file(path_checksum)
    download_yaml_data = load_yaml_file(path_download)

    if component != 'all':
        if component in component_info:
            logging.info(f'Processing specified component: {component}')
            process_component(component, component_info[component], session)
        else:
            logging.error(f'Component {component} not found in config.')
            return
    else:
        with ThreadPoolExecutor(max_workers = maxworkers) as executor:
            futures = []
            logging.info(f'Running with {executor._max_workers} executors')
            for component, component_data in component_info.items():
                futures.append(executor.submit(process_component, component, component_data, session))
            for future in futures:
                future.result()

    save_yaml_file(path_checksum, checksum_yaml_data)
    save_yaml_file(path_download, download_yaml_data)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Component version updater with logging and concurrency.')
    parser.add_argument('--loglevel', default='INFO', help='Set the log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)')
    parser.add_argument('--maxworkers', type=int, default=4, help='Maximum number of concurrent workers, use with caution')
    parser.add_argument('--skip-if-up-to-date', action='store_true', help='Skip processing component if the current version is up to date')
    parser.add_argument('--component', default='all', help='Specify a component to process, default is all components')

    args = parser.parse_args()

    main(args.loglevel, args.maxworkers, args.component)