import os
import re
import json
import time
import logging
import tempfile
import hashlib
import argparse
import requests
from ruamel.yaml import YAML
from ruamel.yaml.error import YAMLError
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from io import StringIO
from config import component_info, architectures, oses, path_download, path_checksum, path_main




def get_session_with_retries(retries=5, backoff_factor=0.3, status_forcelist=(500, 502, 503, 504)):
    session = requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


session = get_session_with_retries()
yaml = YAML()
yaml.explicit_start = True
yaml.preserve_quotes = True
yaml.width = 4096
yaml.indent(mapping=2, sequence=4, offset=2)


def setup_logging(loglevel):
    numeric_level = getattr(logging, loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {loglevel}")
    logging.basicConfig(level=numeric_level, format='%(asctime)s - %(levelname)s - %(message)s')


def download_file(url, session):
    try:
        response = session.get(url, timeout=10)
        response.raise_for_status()

        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(response.content)
            tmp_file_path = tmp_file.name

        logging.info(f"Downloaded file from {url} to {tmp_file_path}")
        return tmp_file_path
    except requests.exceptions.RequestException as e:
        logging.warning(f"Failed to download {url}: {e}")
        return None


def calculate_checksum(file_path, checksum_type='sha256'):
    hasher = hashlib.new(checksum_type)

    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)

        return hasher.hexdigest()
    except Exception as e:
        logging.error(f"Error calculating checksum for {file_path}: {e}")
        return None
    

def cache_release_info(component, release_url, session):
    cache_dir = 'cache'
    cache_file = os.path.join(cache_dir, f'{component}.json')
    cache_expiry = 86400

    os.makedirs(cache_dir, exist_ok=True)

    if os.path.exists(cache_file):
        file_age = time.time() - os.path.getmtime(cache_file)
        if file_age < cache_expiry:
            logging.debug(f"Reading cached release info for {component}")
            with open(cache_file, 'r') as file:
                return json.load(file)

    try:
        logging.debug(f"Fetching release info for {component} from {release_url}")
        response = session.get(release_url, timeout=10)
        response.raise_for_status()

        try:
            release_info = response.json()
        except json.JSONDecodeError:
            release_info = {"tag_name": response.text}

        with open(cache_file, 'w') as file:
            file.write(json.dumps(release_info, indent=2))

        return release_info

    except requests.exceptions.RequestException as e:
        logging.error(f"An error occurred while fetching release info for {component}: {e}")

    return None


def get_latest_version(component, release_info):
    latest_version = None

    if isinstance(release_info, dict):
        latest_version = release_info.get("tag_name", None)

    if not latest_version and isinstance(release_info, list):
        try:
            latest_version = release_info[0]["name"]
            latest_version = re.sub(r'^release-([0-9]+).*', r'\1', latest_version)
        except:
            latest_version = None

    if isinstance(latest_version, str) and component in ["youki", "nerdctl", "cri_dockerd", "containerd"]:
        latest_version = latest_version.lstrip("v")

    return latest_version


def load_yaml_file(yaml_file):
    try:
        with open(yaml_file, "r") as f:
            return yaml.load(f) or {}
    except YAMLError as e:
        logging.error(f"Error while parsing YAML file {yaml_file}: {e}")
        return None
    except FileNotFoundError:
        logging.warning(f"YAML file {yaml_file} not found, initializing empty structure.")
        return {}


def save_yaml_file(yaml_file, data):
    try:
        with open(yaml_file, "w") as f:
            yaml.dump(data, f)
    except Exception as e:
        logging.error(f"Error while saving YAML file {yaml_file}: {e}")


def get_yaml_value(yaml_file, keys):
    data = load_yaml_file(yaml_file)
    if len(keys) == 1:
        key = keys[0]
        data = data[key]
    else:
        for key in keys:
            if isinstance(data, dict) and key in data:
                data = data[key]    
    return data


def post_process_yaml(yaml_content):
    pattern = re.compile(r"'(\d+(\.\d+)*)'")
    processed_yaml = pattern.sub(r"\1", yaml_content)
    return processed_yaml


def update_yaml_value(yaml_file, keys, value):
    data = load_yaml_file(yaml_file)
    if not data:
        return

    current = data
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]

    final_key = keys[-1]
    new_entry = {final_key: value}
    
    if final_key in current:
        current[final_key] = value
    else:
        if isinstance(current, dict):
            current = {**new_entry, **current}

    if len(keys) > 1:
        parent = data
        for key in keys[:-2]:
            parent = parent.get(key, {})
        parent[keys[-2]] = current

    logging.info(f"Updating {keys} with value {value}")

    yaml_buffer = StringIO()
    yaml.dump(data, yaml_buffer)
    yaml_content = yaml_buffer.getvalue()
    processed_yaml = post_process_yaml(yaml_content)

    with open(yaml_file, 'w') as f:
        f.write(processed_yaml)
    
    yaml_buffer = StringIO(processed_yaml)
    data = yaml.load(yaml_buffer)
    save_yaml_file(yaml_file, data)

    logging.debug(f"Updated and post-processed YAML written to {yaml_file}")


def get_component_checksums(component, download_url, arch, version, session):
    if component in ["gvisor_runsc", "gvisor_containerd_shim"]:
        tmp_arch = arch.replace("arm64", "aarch64").replace("amd64", "x86_64")
    elif component == "youki":
        tmp_arch = arch.replace("arm64", "aarch64-gnu").replace("amd64", "x86_64-gnu")
    else:
        tmp_arch = arch

    tmp_download_url = download_url.replace("VERSION", version).replace("ARCH", tmp_arch)
    logging.debug(f"Downloading file {tmp_download_url}")

    tmp_file_path = download_file(tmp_download_url, session)
    if tmp_file_path is None:
        return None

    if download_url.endswith((".sha256", ".sha256sum")):
        try:
            with open(tmp_file_path, 'r') as f:
                content = f.read().strip()
                sha256 = content.split()[0] if content else None
            os.remove(tmp_file_path)
            return sha256
        except Exception as e:
            logging.error(f"Error reading checksum file {tmp_file_path}: {e}")
            os.remove(tmp_file_path)
            return None

    sha256 = calculate_checksum(tmp_file_path)
    os.remove(tmp_file_path)
    return sha256


def process_checksums(component, download_url, checksum_placeholder, architectures, latest_version, path_checksum, session, oses=None):
    if component == 'krew':
        for os in oses:
            tmp_download_url = download_url.replace("OS", os)
            for arch in architectures:
                checksum = get_component_checksums(component, tmp_download_url, arch, latest_version, session)
                if checksum:
                    update_yaml_value(path_checksum, checksum_placeholder + [os, arch, latest_version], checksum)
                else:
                    update_yaml_value(path_checksum, checksum_placeholder + [os, arch, latest_version], 0)
    elif component == 'calico_crds':
        checksum = get_component_checksums(component, download_url, '', latest_version, session)
        if checksum:
            update_yaml_value(path_checksum, checksum_placeholder + [latest_version], checksum)
        else:
            update_yaml_value(path_checksum, checksum_placeholder + [latest_version], 0)
    else:
        for arch in architectures:
            checksum = get_component_checksums(component, download_url, arch, latest_version, session)
            if checksum:
                update_yaml_value(path_checksum, checksum_placeholder + [arch, latest_version], checksum)
            else:
                update_yaml_value(path_checksum, checksum_placeholder + [arch, latest_version], 0)


def process_component(component, component_data, path_main, path_download, path_checksum, architectures, oses, session):
    logging.info(f"Processing component {component}")
    release_url = component_data['release_url']
    download_url = component_data['download_url']
    checksum_placeholder = component_data['checksum_placeholder']

    kube_version = get_yaml_value(path_main, ['kube_version'])
    kube_major_version = '.'.join(kube_version.split('.')[:2])

    version_placeholder = [kube_major_version if item == 'kube_major_version' else item for item in component_data['version_placeholder']]

    release_info = cache_release_info(component, release_url, session)
    if not release_info:
        logging.warning(f"Skipping {component} due to missing release info.")
        return

    if component.startswith('kube'):
        current_version = get_yaml_value(path_main, version_placeholder)
    else:
        current_version = get_yaml_value(path_download, version_placeholder)
    latest_version = get_latest_version(component, release_info)
    logging.info(f"Component {component} version, current: {current_version}, latest: {latest_version}")


    process_checksums(component, download_url, checksum_placeholder, architectures, latest_version, path_checksum, session, oses)

    if not component.startswith('kube'):
        logging.info(f"Updating {component} version to {latest_version}")
        update_yaml_value(path_download, version_placeholder, latest_version)



def main(loglevel):
    setup_logging(loglevel)

    logging.debug("Starting main loop over components.")
    for component, component_data in component_info.items():
        process_component(component, component_data, path_main, path_download, path_checksum, architectures, oses, session)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Component version updater.')
    parser.add_argument('--loglevel', default='INFO', help='Set the log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)')

    args = parser.parse_args()

    main(args.loglevel)
