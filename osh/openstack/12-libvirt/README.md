# Libvirt

This guide provides instructions to deploy Libvirt service on a Compute nodes.

**Note:** You can use the manifests from this repository as an example and update the details according to your requirements.

**Note:** 
- We will use the CEPH rbd pool `cinder.volumes.gold` and rbd client `rbd-client` created while deploying `CEPH`.
- `rbd-client1` Kubernetes secret is already created while deploying Cinder.
- `ceph-etc` Kubernetes configmap is already created while deploying Cinder

1. Generate the manifests using helm template:
```bash
helm template libvirt ../../openstack-helm-infra/libvirt \
    -f values.yaml \
    --set conf.ceph.cinder.keyring="$(kubectl get secret rook-ceph-client-rbd-client -o jsonpath='{.data.rbd-client}' -n rook-ceph |base64 -d)"
    -n openstack --output-dir manifests
```

2. Extract the Kubernetes secret resource from the manifest files:
```bash
python3 ../../../tools/extract_secrets.py  manifests/
```

3. Encrypt the secrets using kubeseal:
```bash
bash ../../../tools/kubeseal_secret.sh  manifests/ ../../../tools/sealed-secret-tls.crt
```

4. Create the final `kustomization.yaml`:
**Note:** Make sure you remove plain text Kubernetes secret resources from `kustomization.yaml`.
```bash
cat kustomization.yaml
```

5. Commit and push the changes to your Git repository.

6. Apply the ArgoCD application to deploy Keystone.
```bash
kubectl  apply -f osh/argoCD/12-libvirt-argo.yaml
```

---

## Validation:
```bash
kubectl get pods -n openstack |egrep -i libvirt
```

ArgoCD continuously monitors the configured Git repository for changes and automatically applies them to the Kubernetes cluster. Once the changes are pushed to the repository, ArgoCD will detect the update and synchronize with the latest version.

Check the ArgoCD UI to track the synchronization progress and ensure that the modifications are successfully applied to the cluster.