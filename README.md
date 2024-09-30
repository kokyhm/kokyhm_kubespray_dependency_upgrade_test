
Note: Upstart/SysV init based OS types are not supported.

## Supported Components

- Core
  - [kubernetes](https://github.com/kubernetes/kubernetes) v1.30.4
  - [etcd](https://github.com/etcd-io/etcd) v3.5.16
  - [docker](https://www.docker.com/) v26.1
  - [containerd](https://containerd.io/) v1.7.21
  - [cri-o](http://cri-o.io/) v1.30.3 (experimental: see [CRI-O Note](docs/CRI/cri-o.md). Only on fedora, ubuntu and centos based OS)
- Network Plugin
  - [cni-plugins](https://github.com/containernetworking/plugins) v1.2.0
  - [calico](https://github.com/projectcalico/calico) v3.28.1
  - [cilium](https://github.com/cilium/cilium) v1.15.4
  - [flannel](https://github.com/flannel-io/flannel) v0.22.0
  - [kube-ovn](https://github.com/alauda/kube-ovn) v1.12.21
  - [kube-router](https://github.com/cloudnativelabs/kube-router) v2.0.0
  - [multus](https://github.com/k8snetworkplumbingwg/multus-cni) v3.8
  - [weave](https://github.com/rajch/weave) v2.8.7
  - [kube-vip](https://github.com/kube-vip/kube-vip) v0.8.0
- Application
  - [cert-manager](https://github.com/jetstack/cert-manager) v1.14.7
  - [coredns](https://github.com/coredns/coredns) v1.11.1
  - [ingress-nginx](https://github.com/kubernetes/ingress-nginx) v1.11.2
  - [krew](https://github.com/kubernetes-sigs/krew) v0.4.4
  - [argocd](https://argoproj.github.io/) v2.11.0
  - [helm](https://helm.sh/) v3.15.4
  - [metallb](https://metallb.universe.tf/)  v0.13.9
  - [registry](https://github.com/distribution/distribution) v2.8.1
- Storage Plugin
  - [cephfs-provisioner](https://github.com/kubernetes-incubator/external-storage) v2.1.0-k8s1.11
  - [rbd-provisioner](https://github.com/kubernetes-incubator/external-storage) v2.1.1-k8s1.11
  - [aws-ebs-csi-plugin](https://github.com/kubernetes-sigs/aws-ebs-csi-driver) v0.5.0
  - [azure-csi-plugin](https://github.com/kubernetes-sigs/azuredisk-csi-driver) v1.10.0
  - [cinder-csi-plugin](https://github.com/kubernetes/cloud-provider-openstack/blob/master/docs/cinder-csi-plugin/using-cinder-csi-plugin.md) v1.30.0
  - [gcp-pd-csi-plugin](https://github.com/kubernetes-sigs/gcp-compute-persistent-disk-csi-driver) v1.9.2
  - [local-path-provisioner](https://github.com/rancher/local-path-provisioner) v0.0.24
  - [local-volume-provisioner](https://github.com/kubernetes-sigs/sig-storage-local-static-provisioner) v2.5.0
  - [node-feature-discovery](https://github.com/kubernetes-sigs/node-feature-discovery) v0.16.4

## Container Runtime Notes

- The cri-o version should be aligned with the respective kubernetes version (i.e. kube_version=1.20.x, crio_version=1.20)

## Requirements

