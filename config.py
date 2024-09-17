component_info = {
    'calico_crds': {
        'url_release' : 'https://api.github.com/repos/projectcalico/calico/releases/latest',
        'url_download': 'https://github.com/projectcalico/calico/archive/VERSION.tar.gz',
        'placeholder_version': ['calico_version'],
        'placeholder_checksum' : 'calico_crds_archive_checksums',
        'checksum_structure' : 'simple',
        },
    'calicoctl': {
        'url_release' : 'https://api.github.com/repos/projectcalico/calico/releases/latest',
        'url_download': 'https://github.com/projectcalico/calico/releases/download/VERSION/calicoctl-linux-ARCH',
        'placeholder_version': ['calico_version'],
        'placeholder_checksum' : 'calicoctl_binary_checksums',
        'checksum_structure' : 'arch',
        },
    'ciliumcli': {
        'url_release' : 'https://api.github.com/repos/cilium/cilium-cli/releases/latest',
        'url_download': 'https://github.com/cilium/cilium-cli/releases/download/VERSION/cilium-linux-ARCH.tar.gz.sha256sum',
        'placeholder_version': ['cilium_cli_version'],
        'placeholder_checksum' : 'ciliumcli_binary_checksums',
        'checksum_structure' : 'arch',
        },
    'cni': {
        'url_release' : 'https://api.github.com/repos/containernetworking/plugins/releases/latest',
        'url_download': 'https://github.com/containernetworking/plugins/releases/download/VERSION/cni-plugins-linux-ARCH-VERSION.tgz.sha256',
        'placeholder_version': ['cni_version'],
        'placeholder_checksum' : 'cni_binary_checksums',
        'checksum_structure' : 'arch',
        },
    'containerd': {
        'url_release' : 'https://api.github.com/repos/containerd/containerd/releases/latest',
        'url_download': 'https://github.com/containerd/containerd/releases/download/vVERSION/containerd-VERSION-linux-ARCH.tar.gz.sha256sum',
        'placeholder_version': ['containerd_version'],
        'placeholder_checksum' : 'containerd_archive_checksums',
        'checksum_structure' : 'arch',
        },
    'crictl': {
        'url_release' : 'https://api.github.com/repos/kubernetes-sigs/cri-tools/releases/latest',
        'url_download': 'https://github.com/kubernetes-sigs/cri-tools/releases/download/VERSION/crictl-VERSION-linux-ARCH.tar.gz.sha256',
        'placeholder_version': ['crictl_supported_versions', 'kube_major_version'],
        'placeholder_checksum' : 'crictl_checksums',
        'checksum_structure' : 'arch',
        },
    'cri_dockerd': {
        'url_release' : 'https://api.github.com/repos/Mirantis/cri-dockerd/releases/latest',
        'url_download': 'https://github.com/Mirantis/cri-dockerd/releases/download/vVERSION/cri-dockerd-VERSION.ARCH.tgz',
        'placeholder_version': ['cri_dockerd_version'],
        'placeholder_checksum' : 'cri_dockerd_archive_checksums',
        'checksum_structure' : 'arch',
        },
    'crio': {
        'url_release' : 'https://api.github.com/repos/cri-o/cri-o/releases/latest',
        'url_download': 'https://storage.googleapis.com/cri-o/artifacts/cri-o.ARCH.VERSION.tar.gz',
        'placeholder_version': ['crio_supported_versions', 'kube_major_version'],
        'placeholder_checksum' : 'crio_archive_checksums',
        'checksum_structure' : 'arch',
        },
    'crun': {
        'url_release' : 'https://api.github.com/repos/containers/crun/releases/latest',
        'url_download': 'https://github.com/containers/crun/releases/download/VERSION/crun-VERSION-linux-ARCH',
        'placeholder_version': ['crun_version'],
        'placeholder_checksum' : 'crun_checksums',
        'checksum_structure' : 'arch',
        },
    'etcd': {
        'url_release' : 'https://api.github.com/repos/etcd-io/etcd/releases/latest',
        'url_download': 'https://github.com/etcd-io/etcd/releases/download/VERSION/SHA256SUMS',
        'placeholder_version': ['etcd_supported_versions', 'kube_major_version'],
        'placeholder_checksum' : 'etcd_binary_checksums',
        'checksum_structure' : 'arch',
        },
    'gvisor_containerd_shim': {
        'url_release' : 'https://api.github.com/repos/google/gvisor/tags',
        'url_download': 'https://storage.googleapis.com/gvisor/releases/release/VERSION/ARCH/containerd-shim-runsc-v1',
        'placeholder_version': ['gvisor_version'],
        'placeholder_checksum' : 'gvisor_containerd_shim_binary_checksums',
        'checksum_structure' : 'arch',
        },
    'gvisor_runsc': {
        'url_release' : 'https://api.github.com/repos/google/gvisor/tags',
        'url_download': 'https://storage.googleapis.com/gvisor/releases/release/VERSION/ARCH/runsc',
        'placeholder_version': ['gvisor_version'],
        'placeholder_checksum' : 'gvisor_runsc_binary_checksums',
        'checksum_structure' : 'arch',
        },
    'helm': {
        'url_release' : 'https://api.github.com/repos/helm/helm/releases/latest',
        'url_download': 'https://get.helm.sh/helm-VERSION-linux-ARCH.tar.gz',
        'placeholder_version': ['helm_version'],
        'placeholder_checksum' : 'helm_archive_checksums',
        'checksum_structure' : 'arch',
        },
    'kata_containers': {
        'url_release' : 'https://api.github.com/repos/kata-containers/kata-containers/releases/latest',
        'url_download': 'https://github.com/kata-containers/kata-containers/releases/download/VERSION/kata-static-VERSION-ARCH.tar.xz',
        'placeholder_version': ['kata_containers_version'],
        'placeholder_checksum' : 'kata_containers_binary_checksums',
        'checksum_structure' : 'arch',
        },
    'krew': {
        'url_release' : 'https://api.github.com/repos/kubernetes-sigs/krew/releases/latest',
        'url_download': 'https://github.com/kubernetes-sigs/krew/releases/download/VERSION/krew-OS_ARCH.tar.gz.sha256',
        'placeholder_version': ['krew_version'],
        'placeholder_checksum' : 'krew_archive_checksums',
        'checksum_structure' : 'os_arch',
        },
    'kubeadm': {
        'url_release' : 'https://storage.googleapis.com/kubernetes-release/release/stable.txt',
        'url_download': 'https://dl.k8s.io/release/VERSION/bin/linux/ARCH/kubeadm.sha256',
        'placeholder_version': ['kube_version'],
        'placeholder_checksum' : 'kubeadm_checksums',
        'checksum_structure' : 'arch',
        },
    'kubectl': {
        'url_release' : 'https://storage.googleapis.com/kubernetes-release/release/stable.txt',
        'url_download': 'https://dl.k8s.io/release/VERSION/bin/linux/ARCH/kubectl.sha256',
        'placeholder_version': ['kube_version'],
        'placeholder_checksum' : 'kubectl_checksums',
        'checksum_structure' : 'arch',
        },
    'kubelet': {
        'url_release' : 'https://storage.googleapis.com/kubernetes-release/release/stable.txt',
        'url_download': 'https://dl.k8s.io/release/VERSION/bin/linux/ARCH/kubelet.sha256',
        'placeholder_version': ['kube_version'],
        'placeholder_checksum' : 'kubelet_checksums',
        'checksum_structure' : 'arch',
        },
    'nerdctl': {
        'url_release' : 'https://api.github.com/repos/containerd/nerdctl/releases/latest',
        'url_download': 'https://github.com/containerd/nerdctl/releases/download/vVERSION/SHA256SUMS',
        'placeholder_version': ['nerdctl_version'],
        'placeholder_checksum' : 'nerdctl_archive_checksums',
        'checksum_structure' : 'arch',
        },
    'runc': {
        'url_release' : 'https://api.github.com/repos/opencontainers/runc/releases/latest',
        'url_download': 'https://github.com/opencontainers/runc/releases/download/VERSION/runc.ARCH',
        'placeholder_version': ['runc_version'],
        'placeholder_checksum' : 'runc_checksums',
        'checksum_structure' : 'arch',
        },
    'skopeo': {
        'url_release' : 'https://api.github.com/repos/containers/skopeo/releases/latest',
        'url_download': 'https://github.com/lework/skopeo-binary/releases/download/VERSION/skopeo-linux-ARCH',
        'placeholder_version': ['skopeo_version'],
        'placeholder_checksum' : 'skopeo_binary_checksums',
        'checksum_structure' : 'arch',
        },
    'youki': {
        'url_release' : 'https://api.github.com/repos/containers/youki/releases/latest',
        'url_download': 'https://github.com/containers/youki/releases/download/vVERSION/youki-VERSION-ARCH.tar.gz',
        'placeholder_version': ['youki_version'],
        'placeholder_checksum' : 'youki_checksums',
        'checksum_structure' : 'arch',
        },
    'yq': {
        'url_release' : 'https://api.github.com/repos/mikefarah/yq/releases/latest',
        'url_download': 'https://github.com/mikefarah/yq/releases/download/VERSION/checksums-bsd',
        'placeholder_version': ['yq_version'],
        'placeholder_checksum' : 'yq_checksums',
        'checksum_structure' : 'arch',
        },
}

# Arhitectures and OSes
architectures = ["arm", "arm64", "amd64", "ppc64le"]
oses = ["darwin", "linux", "windows"]

# Paths
path_download = "roles/kubespray-defaults/defaults/main/download.yml"
path_checksum = "roles/kubespray-defaults/defaults/main/checksums.yml"
path_main = "roles/kubespray-defaults/defaults/main/main.yml"