# CEPH-ROOK: Ceph Integration for Kubernetes
Make Ceph storage work seamlessly with your Kubernetes setup using CEPH-ROOK. It lets Kubernetes nodes use Ceph effortlessly, connecting with both ceph-csi and openstack-helm.

## Pre-installation Checks:
Before proceeding with the Ceph-ROOK installation, ensure the following prerequisites:

- Ensure that Kubernetes nodes are correctly labeled to designate their roles and Ceph components.
```
role: storage-node
ceph-rgw: enabled
ceph-mds: enabled
```
- OSD disks are formatted
- ArgoCD is up and running as expected. 
- Git repository is connected to the ArgoCD. Refer to [\[1\]](https://argo-cd.readthedocs.io/en/stable/user-guide/private-repositories/)[\[2\]](https://argo-cd.readthedocs.io/en/latest/user-guide/commands/argocd_repo_add/)

## Installation:
To install CEPH according as per your requirement, navigate to the CEPH directory, make the necessary modifications to Kubernetes manifest/values.yaml, and deploy it using ArgoCD. You can kickstart your setup by copying the provided examples from this repository.

**Note:** You can use the manifests from this repository as an example and update the details according to your requirements.

- Clone this repository and navigate to the ceph-rook directory:
```bash
git clone --recurse-submodules https://github.com/pratik705/trinity.git
cd trinity/ceph-rook/
```
Note: The `--recurse-submodules` option is used to clone the repository along with its submodules.
- Once you have made your changes, commit and push them to your Git repository.
```bash
git add .
git commit -m "Describe your changes"
git push origin main
```
- Proceed with applying ArgoCD manifests:
### Deploy namespace for CEPH installation:
```bash
kubectl apply -f ceph-rook/argoCD/00-ceph-namespace-argo.yaml
```
---

### Deploy ceph-operator:
```bash
kubectl apply -f ceph-rook/argoCD/01-ceph-operator-argo.yaml
```
---

### Deploy CEPH:
```bash
kubectl apply -f ceph-rook/argoCD/02-ceph-argo.yaml
```
- Sets up a storage class(`general`) for creating rbd volumes.
- Creates an rbd client and pool for openstack-helm.

#### Validation:
```bash
kubectl get cephcluster -n rook-ceph
```

---

### Deploy ceph-rgw:
```bash
kubectl apply -f ceph-rook/argoCD/03-ceph-rgw-argo.yaml
```
#### Validation:
```bash
kubectl get cephobjectstore -n rook-ceph
```

---

### Deploy ceph-mds:
```bash
kubectl apply -f ceph-rook/argoCD/04-ceph-mds-argo.yaml
```
- Adds a storage class(`rook-cephfs`) for creating `rwx` volumes.

#### Validation:
```bash
kubectl get cephfilesystems -n rook-ceph
```

---

### Deploy toolbox to interact with CEPH:
```bash
kubectl apply -f ceph-rook/argoCD/05-toolbox-argo.yaml
```
---

## Validation:
```bash
kubectl get pods -n rook-ceph
kubectl exec -it rook-ceph-tools-xxxxx -n rook-ceph -- ceph -s
kubectl exec -it rook-ceph-tools-xxxxx -n rook-ceph -- ceph osd tree
```

---

![ceph](../screenshots/ceph_argocd.jpg?raw=true)

ArgoCD continuously monitors the configured Git repository for changes and automatically applies them to the Kubernetes cluster. Once the changes are pushed to the repository, ArgoCD will detect the update and synchronize with the latest version.

Check the ArgoCD UI to track the synchronization progress and ensure that the modifications are successfully applied to the cluster.