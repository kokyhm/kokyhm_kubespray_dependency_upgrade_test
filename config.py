component_info = {
    'calico_crds': {
        'release_url' : 'https://api.github.com/repos/projectcalico/calico/releases/latest',
        'download_url': 'https://github.com/projectcalico/calico/archive/VERSION.tar.gz',
        'version_placeholder': ['calico_version'],
        'checksum_placeholder' : ['calico_crds_archive_checksums'],
        },
    'calicoctl': {
        'release_url' : 'https://api.github.com/repos/projectcalico/calico/releases/latest',
        'download_url': 'https://github.com/projectcalico/calico/releases/download/VERSION/calicoctl-linux-ARCH',
        'version_placeholder': ['calico_version'],
        'checksum_placeholder' : ['calicoctl_binary_checksums'],
        },
    'ciliumcli': {
        'release_url' : 'https://api.github.com/repos/cilium/cilium-cli/releases/latest',
        'download_url': 'https://github.com/cilium/cilium-cli/releases/download/VERSION/cilium-linux-ARCH.tar.gz.sha256sum',
        'version_placeholder': ['cilium_cli_version'],
        'checksum_placeholder' : ['ciliumcli_binary_checksums'],
        },
    'cni': {
        'release_url' : 'https://api.github.com/repos/containernetworking/plugins/releases/latest',
        'download_url': 'https://github.com/containernetworking/plugins/releases/download/VERSION/cni-plugins-linux-ARCH-VERSION.tgz.sha256',
        'version_placeholder': ['cni_version'],
        'checksum_placeholder' : ['cni_binary_checksums'],
        },
    'containerd': {
        'release_url' : 'https://api.github.com/repos/containerd/containerd/releases/latest',
        'download_url': 'https://github.com/containerd/containerd/releases/download/vVERSION/containerd-VERSION-linux-ARCH.tar.gz.sha256sum',
        'version_placeholder': ['containerd_version'],
        'checksum_placeholder' : ['containerd_archive_checksums'],
        },
    'crictl': {
        'release_url' : 'https://api.github.com/repos/kubernetes-sigs/cri-tools/releases/latest',
        'download_url': 'https://github.com/kubernetes-sigs/cri-tools/releases/download/VERSION/crictl-VERSION-linux-ARCH.tar.gz.sha256',
        'version_placeholder': ['crictl_supported_versions', 'kube_major_version'],
        'checksum_placeholder' : ['crictl_checksums'],
        },
    'cri_dockerd': {
        'release_url' : 'https://api.github.com/repos/Mirantis/cri-dockerd/releases/latest',
        'download_url': 'https://github.com/Mirantis/cri-dockerd/releases/download/vVERSION/cri-dockerd-VERSION.ARCH.tgz',
        'version_placeholder': ['cri_dockerd_version'],
        'checksum_placeholder' : ['cri_dockerd_archive_checksums'],
        },
    'crio': {
        'release_url' : 'https://api.github.com/repos/cri-o/cri-o/releases/latest',
        'download_url': 'https://storage.googleapis.com/cri-o/artifacts/cri-o.ARCH.VERSION.tar.gz',
        'version_placeholder': ['crio_supported_versions', 'kube_major_version'],
        'checksum_placeholder' : ['crio_archive_checksums'],
        },
    'crun': {
        'release_url' : 'https://api.github.com/repos/containers/crun/releases/latest',
        'download_url': 'https://github.com/containers/crun/releases/download/VERSION/crun-VERSION-linux-ARCH',
        'version_placeholder': ['crun_version'],
        'checksum_placeholder' : ['crun_checksums'],
        },
    'etcd': {
        'release_url' : 'https://api.github.com/repos/etcd-io/etcd/releases/latest',
        'download_url': 'https://github.com/etcd-io/etcd/releases/download/VERSION/etcd-VERSION-linux-ARCH.tar.gz',
        'version_placeholder': ['etcd_supported_versions', 'kube_major_version'],
        'checksum_placeholder' : ['etcd_binary_checksums'],
        },
    'gvisor_containerd_shim': {
        'release_url' : 'https://api.github.com/repos/google/gvisor/tags',
        'download_url': 'https://storage.googleapis.com/gvisor/releases/release/VERSION/ARCH/containerd-shim-runsc-v1',
        'version_placeholder': ['gvisor_version'],
        'checksum_placeholder' : ['gvisor_containerd_shim_binary_checksums'],
        },
    'gvisor_runsc': {
        'release_url' : 'https://api.github.com/repos/google/gvisor/tags',
        'download_url': 'https://storage.googleapis.com/gvisor/releases/release/VERSION/ARCH/runsc',
        'version_placeholder': ['gvisor_version'],
        'checksum_placeholder' : ['gvisor_runsc_binary_checksums'],
        },
    'helm': {
        'release_url' : 'https://api.github.com/repos/helm/helm/releases/latest',
        'download_url': 'https://get.helm.sh/helm-VERSION-linux-ARCH.tar.gz',
        'version_placeholder': ['helm_version'],
        'checksum_placeholder' : ['helm_archive_checksums'],
        },
    'kata_containers': {
        'release_url' : 'https://api.github.com/repos/kata-containers/kata-containers/releases/latest',
        'download_url': 'https://github.com/kata-containers/kata-containers/releases/download/VERSION/kata-static-VERSION-ARCH.tar.xz',
        'version_placeholder': ['kata_containers_version'],
        'checksum_placeholder' : ['kata_containers_binary_checksums'],
        },
    'krew': {
        'release_url' : 'https://api.github.com/repos/kubernetes-sigs/krew/releases/latest',
        'download_url': 'https://github.com/kubernetes-sigs/krew/releases/download/VERSION/krew-OS_ARCH.tar.gz.sha256',
        'version_placeholder': ['krew_version'],
        'checksum_placeholder' : ['krew_archive_checksums'],
        },
    'kubeadm': {
        'release_url' : 'https://storage.googleapis.com/kubernetes-release/release/stable.txt',
        'download_url': 'https://dl.k8s.io/release/VERSION/bin/linux/ARCH/kubeadm.sha256',
        'version_placeholder': ['kube_version'],
        'checksum_placeholder' : ['kubeadm_checksums'],
        },
    'kubectl': {
        'release_url' : 'https://storage.googleapis.com/kubernetes-release/release/stable.txt',
        'download_url': 'https://dl.k8s.io/release/VERSION/bin/linux/ARCH/kubectl.sha256',
        'version_placeholder': ['kube_version'],
        'checksum_placeholder' : ['kubectl_checksums'],
        },
    'kubelet': {
        'release_url' : 'https://storage.googleapis.com/kubernetes-release/release/stable.txt',
        'download_url': 'https://dl.k8s.io/release/VERSION/bin/linux/ARCH/kubelet.sha256',
        'version_placeholder': ['kube_version'],
        'checksum_placeholder' : ['kubelet_checksums'],
        },
    'nerdctl': {
        'release_url' : 'https://api.github.com/repos/containerd/nerdctl/releases/latest',
        'download_url': 'https://github.com/containerd/nerdctl/releases/download/vVERSION/nerdctl-VERSION-linux-ARCH.tar.gz',
        'version_placeholder': ['nerdctl_version'],
        'checksum_placeholder' : ['nerdctl_archive_checksums'],
        },
    'runc': {
        'release_url' : 'https://api.github.com/repos/opencontainers/runc/releases/latest',
        'download_url': 'https://github.com/opencontainers/runc/releases/download/VERSION/runc.ARCH',
        'version_placeholder': ['runc_version'],
        'checksum_placeholder' : ['runc_checksums'],
        },
    'skopeo': {
        'release_url' : 'https://api.github.com/repos/containers/skopeo/releases/latest',
        'download_url': 'https://github.com/lework/skopeo-binary/releases/download/VERSION/skopeo-linux-ARCH',
        'version_placeholder': ['skopeo_version'],
        'checksum_placeholder' : ['skopeo_binary_checksums'],
        },
    'youki': {
        'release_url' : 'https://api.github.com/repos/containers/youki/releases/latest',
        'download_url': 'https://github.com/containers/youki/releases/download/vVERSION/youki-VERSION-ARCH.tar.gz',
        'version_placeholder': ['youki_version'],
        'checksum_placeholder' : ['youki_checksums'],
        },
    'yq': {
        'release_url' : 'https://api.github.com/repos/mikefarah/yq/releases/latest',
        'download_url': 'https://github.com/mikefarah/yq/releases/download/VERSION/yq_linux_ARCH',
        'version_placeholder': ['yq_version'],
        'checksum_placeholder' : ['yq_checksums'],
        },
}

# Arhitectures and OSes
architectures = ["arm", "arm64", "amd64", "ppc64le"]
oses = ["darwin", "linux", "windows"]

# Paths
path_download = "roles/kubespray-defaults/defaults/main/download.yml"
path_checksum = "roles/kubespray-defaults/defaults/main/checksums.yml"
path_main = "roles/kubespray-defaults/defaults/main/main.yml"