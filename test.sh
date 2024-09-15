#!/bin/bash
 
# Component release info => component, release_url and download_url
declare -A component_release=(
 [calico_crds]="https://api.github.com/repos/projectcalico/calico/releases/latest https://github.com/projectcalico/calico/archive/VERSION.tar.gz"
 [calicoctl]="https://api.github.com/repos/projectcalico/calico/releases/latest https://github.com/projectcalico/calico/releases/download/VERSION/calicoctl-linux-ARCH"
 [ciliumcli]="https://api.github.com/repos/cilium/cilium-cli/releases/latest https://github.com/cilium/cilium-cli/releases/download/VERSION/cilium-linux-ARCH.tar.gz.sha256sum"
 [cni]="https://api.github.com/repos/containernetworking/plugins/releases/latest https://github.com/containernetworking/plugins/releases/download/VERSION/cni-plugins-linux-ARCH-VERSION.tgz.sha256"
 [containerd]="https://api.github.com/repos/containerd/containerd/releases/latest https://github.com/containerd/containerd/releases/download/vVERSION/containerd-VERSION-linux-ARCH.tar.gz.sha256sum"
 [crictl]="https://api.github.com/repos/kubernetes-sigs/cri-tools/releases/latest https://github.com/kubernetes-sigs/cri-tools/releases/download/VERSION/crictl-VERSION-linux-ARCH.tar.gz.sha256"
 [cri_dockerd]="https://api.github.com/repos/Mirantis/cri-dockerd/releases/latest https://github.com/Mirantis/cri-dockerd/releases/download/vVERSION/cri-dockerd-VERSION.ARCH.tgz"
 [crio]="https://api.github.com/repos/cri-o/cri-o/releases/latest https://storage.googleapis.com/cri-o/artifacts/cri-o.ARCH.VERSION.tar.gz"
 [crun]="https://api.github.com/repos/containers/crun/releases/latest https://github.com/containers/crun/releases/download/VERSION/crun-VERSION-linux-ARCH"
 [etcd]="https://api.github.com/repos/etcd-io/etcd/releases/latest https://github.com/etcd-io/etcd/releases/download/VERSION/etcd-VERSION-linux-ARCH.tar.gz"
 [gvisor_containerd_shim]="https://api.github.com/repos/google/gvisor/tags https://storage.googleapis.com/gvisor/releases/release/VERSION/ARCH/containerd-shim-runsc-v1"
 [gvisor_runsc]="https://api.github.com/repos/google/gvisor/tags https://storage.googleapis.com/gvisor/releases/release/VERSION/ARCH/runsc"
 [helm]="https://api.github.com/repos/helm/helm/releases/latest https://get.helm.sh/helm-VERSION-linux-ARCH.tar.gz"
 [kata_containers]="https://api.github.com/repos/kata-containers/kata-containers/releases/latest https://github.com/kata-containers/kata-containers/releases/download/VERSION/kata-static-VERSION-ARCH.tar.xz"
 [krew]="https://api.github.com/repos/kubernetes-sigs/krew/releases/latest https://github.com/kubernetes-sigs/krew/releases/download/VERSION/krew-OS_ARCH.tar.gz.sha256"
 [kubeadm]="https://storage.googleapis.com/kubernetes-release/release/stable.txt https://dl.k8s.io/release/VERSION/bin/linux/ARCH/kubeadm.sha256"
 [kubectl]="https://storage.googleapis.com/kubernetes-release/release/stable.txt https://dl.k8s.io/release/VERSION/bin/linux/ARCH/kubectl.sha256"
 [kubelet]="https://storage.googleapis.com/kubernetes-release/release/stable.txt https://dl.k8s.io/release/VERSION/bin/linux/ARCH/kubelet.sha256"
 [nerdctl]="https://api.github.com/repos/containerd/nerdctl/releases/latest https://github.com/containerd/nerdctl/releases/download/vVERSION/nerdctl-VERSION-linux-ARCH.tar.gz"
 [runc]="https://api.github.com/repos/opencontainers/runc/releases/latest https://github.com/opencontainers/runc/releases/download/VERSION/runc.ARCH"
 [skopeo]="https://api.github.com/repos/containers/skopeo/releases/latest https://github.com/lework/skopeo-binary/releases/download/VERSION/skopeo-linux-ARCH"
 [youki]="https://api.github.com/repos/containers/youki/releases/latest https://github.com/containers/youki/releases/download/vVERSION/youki-VERSION-ARCH.tar.gz"
 [yq]="https://api.github.com/repos/mikefarah/yq/releases/latest https://github.com/mikefarah/yq/releases/download/VERSION/yq_linux_ARCH"
)


architectures=("arm" "arm64") # "amd64" "ppc64le")
oses=("linux" "darwin" "windows")
path_main="roles/kubespray-defaults/defaults/main/main.yml"
path_download="roles/kubespray-defaults/defaults/main/download.yml"
path_checksum="roles/kubespray-defaults/defaults/main/checksums.yml"
kube_major_version=$(yq ".kube_version" "$path_main" | sed -E 's/^v([0-9]+)\.([0-9]+)\.[0-9]+/v\1.\2/')


# Get release info
function cache_release_info() {
  local component="$1"
  local release_url="$2"
  local cache_file="cache/$component.json"
  local cache_expiry=86400  # 1 day

  mkdir -p cache

  # use cached file if it's still valid
  if [[ -f "$cache_file" && $(find "$cache_file" -mmin -$((cache_expiry / 60))) ]]; then
    cat "$cache_file"
  else
    # fetch new release info and cache it
    release_info=$(curl -sL "$release_url")
    echo "$release_info" > "$cache_file"
    echo "$release_info"
  fi
}


# Get latest version
function get_latest_version() {
  local release_info="$1"
  local latest_version

  # generic
  latest_version=$(echo "$release_info" | jq -r ".tag_name" 2>/dev/null)
  # gvisor
  if [[ -z "$latest_version" ]]; then
      latest_version=$(echo "$release_info" | jq -r ".[0].name" 2>/dev/null | sed -E 's|^release-([0-9]+).*|\1|')
  fi
  # kube
  if [[ -z "$latest_version" ]]; then
      latest_version=$release_info
  fi
  # remove heading v for some components
  if [[ $component == "youki" || $component == "nerdctl"  || $component == "cri_dockerd" || $component == "containerd" ]]; then
    latest_version="${latest_version#v}"
  fi
  echo "$latest_version"
}

# Get current supported version
function get_current_version() {
  local component="$1"
  local current_version
  local version_placeholder
  local version_placeholder_next
  
  version_placeholder=$(get_name_from_placeholder "$(yq ".downloads.$component.version" "$path_download")")
  if [[ $component == kube* ]]; then
    current_version=$(yq ".$version_placeholder" "$path_main")
  elif [[ $component == "calicoctl" ]]; then
    version_placeholder_next=$(get_name_from_placeholder "$(yq ".$version_placeholder" "$path_download")")
    current_version=$(yq ".$version_placeholder_next" "$path_download")
  elif [[ $component == "crictl" || $component == "etcd" || $component == "crio" ]]; then
    version_placeholder_next=$(yq ".$version_placeholder" "$path_download"| sed -E 's/\{\{\s*([^[]+)\[.+\]\s*\}\}/\1/')
    current_version=$(yq ".$version_placeholder_next.\"$kube_major_version\"" "$path_download")
  else
    current_version=$(yq ".$version_placeholder" "$path_download")
  fi
  echo "$current_version"
}


# Get name from placeholder, e.g. extract something from {{ something }}
function get_name_from_placeholder() {
  local placeholder="$1"
  echo "$placeholder" | sed -E 's/\{\{\s*([^}]+)\s*\}\}/\1/'
}


# Check for multiple supported os systems, e.g. component -> os -> arch -> sha
function is_os_component() {
  local component="$1"
  
  if [[ "$component" == "krew" ]]; then
    return 0  # True
  else
    return 1  # False
  fi
}


# Check sha only, e.g. component -> sha
function is_simple_component() {
  local component="$1"
  
  if [[ "$component" == "calico_crds" ]]; then
    return 0  # True
  else
    return 1  # False
  fi
}


# Get checksum of the component for specific arhitecture
function get_checksum_arch() {
  local component="$1"
  local download_url="$2"
  local version="$3"
  local arch="$4"
  local json_data=$5  # JSON data passed by reference

  # Handle naming convention
  if [[ $component == "gvisor_runsc" || $component == "gvisor_containerd_shim" ]]; then
    tmp_arch=${arch/arm64/aarch64} && tmp_arch=${tmp_arch/amd64/x86_64}
  elif [[ "$component" == "youki" ]]; then
    tmp_arch=${arch/arm64/aarch64-gnu} && tmp_arch=${tmp_arch/amd64/x86_64-gnu}
  else
    tmp_arch=$arch
  fi

  # Replace placeholders in download_url
  tmp_download_url="${download_url//VERSION/$version}"
  tmp_download_url="${tmp_download_url//ARCH/$tmp_arch}"

  echo "Download URL: $tmp_download_url" >&2

  tmp_file=$(mktemp) # create tmp_file for download
  if ! curl -fsL "$tmp_download_url" -o "$tmp_file"; then
    sha256=0 # curl failed
  else
    if [[ "$download_url" == *".sha256" || "$download_url" == *".sha256sum" ]]; then
      sha256=$(awk '{print $1}' "$tmp_file") # checksum text file
    else
      sha256=$(sha256sum "$tmp_file" | awk '{print $1}') # binary file
    fi
  fi
  rm -f "$tmp_file"

  # Update the JSON data with the checksum for this architecture
  updated_json=$(echo "$json_data" | jq --arg arch "$arch" --arg sha256 "$sha256" '. + {($arch): $sha256}')
  echo "$updated_json"
}


# Get checksum for each OS and arhitecture
function get_checksum_os_arch() {
  local component="$1"
  local download_url="$2"
  local version="$3"
  local json_data="{}"  # initialize JSON

  for os in "${oses[@]}"; do
    arch_json="{}"  # reset architecture JSON
    for arch in "${architectures[@]}"; do
      tmp_download_url="${download_url//OS/$os}"
      arch_json=$(get_checksum_arch "$component" "$tmp_download_url" "$version" "$arch" "$arch_json")
    done
    # Update JSON for the OS
    json_data=$(echo "$json_data" | jq --arg os "$os" --argjson arch_json "$arch_json" '. + {($os): $arch_json}')
  done

  echo "$json_data"
}


# Update yaml
function update_checksum_value() {
  local checksum_path="$1"
  local version="$2"
  local checksum="$3"

  echo "Checksum Path: ${checksum_path}"
  echo "Version: ${version}"
  echo "Checksum: ${checksum}"
  echo "File Path: ${path_checksum}"

  # Check if the version exists in the YAML
  key_exists=$(yq eval "has(${checksum_path}[${version}])" "$path_checksum")

  if [[ "$key_exists" == "true" ]]; then
    if [[ "$checksum" =~ ^[0-9]+$ ]]; then
      echo "debug 1"
      yq -i "${checksum_path}[${version}] = $checksum" "$path_checksum"
    else
      echo "debug 1"
      yq -i "${checksum_path}[${version}] = \"$checksum\"" "$path_checksum"
    fi
    echo "Updated $version with checksum $checksum in $checksum_path"
  else
    if [[ "$version" =~ ^[0-9]+$ && ! "$checksum" =~ ^[0-9]+$ ]]; then
      echo "debug 3"
      yq -i "${checksum_path} = {${version}: 0} + ${checksum_path}" "$path_checksum"
      yq -i "${checksum_path}[${version}] = \"$checksum\"" "$path_checksum"
    elif [[ "$version" =~ ^[0-9]+$ && "$checksum" =~ ^[0-9]+$ ]]; then
      yq -i "${checksum_path} = {$version: $checksum} + ${checksum_path}" "$path_checksum"
    else
      echo "debug 4"
      yq -i "${checksum_path} = {\"$version\": \"$checksum\"} + ${checksum_path}" "$path_checksum" >/dev/null 2>&1
      echo "Prepended $version with checksum $checksum to $checksum_path"
    fi
  fi
}




# Update checksum
function update_checksum() {
  local component="$1"
  local json_data="$2"
  local version="$3"
  local checksum
  local checksum_path
  local checksum_placeholder

  # Get checksum placeholder
  checksum_placeholder=$(get_name_from_placeholder "$(yq ".downloads.$component.sha256" "$path_download")" | awk '{print $1}')
  checksum_placeholder_next=$(yq ".$checksum_placeholder" "$path_download" | sed -E 's/\{\{\s*([^\[]+)\[.*\]\s*\}\}/\1/')
  
  echo "$json_data" | jq .
  if is_simple_component "$component"; then
    checksum_path=".$checksum_placeholder_next"
    checksum=$(yq ".version" <<< "$json_data")
    update_checksum_value "$checksum_path" "$version" "$checksum"
  elif is_os_component "$component"; then
    for os in "${oses[@]}"; do
      for arch in "${architectures[@]}"; do
        checksum_path=".$checksum_placeholder_next.$os.$arch"
        checksum=$(yq ".$os.$arch" <<< "$json_data")
        update_checksum_value "$checksum_path" "$version" "$checksum"
      done
    done
  else
    for arch in "${architectures[@]}"; do
      checksum=$(yq ".$arch" <<< "$json_data")
      checksum_path=".$checksum_placeholder_next.$arch"
      update_checksum_value "$checksum_path" "$version" "$checksum"
    done
  fi
}


# Update version
function update_version() {
  local component="$1"
  local latest_version="$2"

  if is_os_component "$component"; then
    echo "updating whole os"
  elif is_simple_component "$component"; then
    echo "updating only version"
  else
    echo "updating arhitectures"
  fi
  echo "Component: $component, latest version: $latest_version"
}


# Main function
function process_component() {
  local component="$1"
  local download_url="$2"
  local version="$3"
  local checksums  # JSON data

  if is_os_component "$component"; then
    checksums=$(get_checksum_os_arch "$component" "$download_url" "$version")
  elif is_simple_component "$component"; then
    checksums="{}"
    checksums=$(get_checksum_arch "$component" "$download_url" "$version" "version" "$checksums") # final json will have a version as a key
  else
    checksums="{}"  # initialize JSON for non-OS components
    for arch in "${architectures[@]}"; do
      checksums=$(get_checksum_arch "$component" "$download_url" "$version" "$arch" "$checksums")
    done
  fi

  # Update version
  update_version "$component" "$latest_version"
  # Update checksums
  update_checksum "$component" "$checksums" "$latest_version"
  
}


# Main loop
for component in "${!component_release[@]}"; do
  IFS=' ' read -r -a release_spec <<< "${component_release[$component]}"
  release_url="${release_spec[0]}"
  download_url="${release_spec[1]}"
  release_info=$(cache_release_info "$component" "$release_url")

  latest_version=$(get_latest_version "$release_info")
  current_version=$(get_current_version "$component")
  
  echo -e "Component: $component\nLatest version: $latest_version\nCurrent version: $current_version"
  
  process_component "$component" "$download_url" "$latest_version"
done


