# trinity

The goal of this repository is to simplify the deployment of OpenStack-Helm with ArgoCD, adopting a GitOps approach. The repository offers detailed instructions to deploy following projects:
- RKE2 Kubernetes Cluster
- Managed services:
  - Cert-manager
  - Sealed-secrets
  - Ingress-controller
  - Metallb
  - ArgoCD
- Ceph Rook
- kube-prometheus-stack 
- OpenStack Helm

Sealed-secret will be used to encrypt all plaintext Kubernetes secrets. Therefore, throughout the process, all secrets pushed to the Git repository will be in encrypted format.

The manifests for Ceph-Rook and OpenStack-Helm are sourced from the [Genestack Project](https://github.com/cloudnull/genestack.git), serving as a reference for your deployments.

**Note:** You can use the processes and manifest files from this repository as a reference. Please update the details according to your requirements.

---
## Prerequsites:
Before getting started, make sure you have the following tools installed:
- [kustomize CLI](https://kubectl.docs.kubernetes.io/installation/kustomize/)
- [kubeseal CLI](https://github.com/bitnami-labs/sealed-secrets?tab=readme-ov-file#kubeseal)
- Additionally, ensure that your hardware setup is sufficient to deploy OpenStack and Ceph. In our example, we utilized a total of 8 nodes, each serving a specific role:
  - 3 nodes as OpenStack Controllers
  - 2 nodes as OpenStack Computes
  - 3 nodes for Ceph (ceph-mon, ceph-osd, ceph-mds, ceph-rgw)
---

## Getting started
```bash 
git clone --recurse-submodules https://github.com/pratik705/trinity.git
```
The `--recurse-submodules` option is used to clone the repository along with its submodules.

---

## Installation
To start fresh, please proceed in the following order. If you already have an existing Kubernetes cluster and only want to install specific services, you can jump to the respective section.

### RKE2
Follow the detailed installation instructions [here](https://github.com/pratik705/trinity/blob/main/rke2/README.md).

---

### managed-services
Follow the detailed installation instructions [here](https://github.com/pratik705/trinity/blob/main/managed-services/README.md).

---

### ceph-rook
Follow the detailed installation instructions [here](https://github.com/pratik705/trinity/blob/main/ceph-rook/README.md).

---

### kube-prometheus-stack
Follow the detailed installation instructions [here](https://github.com/pratik705/trinity/blob/main/monitoring/kube-prometheus-stack/README.md).

---

### openstack-helm
Follow the detailed installation instructions [here](https://github.com/pratik705/trinity/blob/main/osh/README.md).

---

These steps will guide you through setting up a Kubernetes environment and deploying ceph-rook, OpenStack-Helm with the necessary supporting services. You can refer the [Genestack Project](https://github.com/cloudnull/genestack.git) for additional insights and resources.

