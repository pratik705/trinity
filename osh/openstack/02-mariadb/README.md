# Mariadb

This guide provides instructions to deploy MariaDB on a Kubernetes cluster. 

**Note:** You can use the manifests from this repository as an example and update the details according to your requirements.


1. Create secret:
```
cd openstack/02-mariadb
kubectl --namespace openstack \
        create secret generic mariadb \
        --dry-run \
        -o yaml \
        --type Opaque \
        --from-literal=root-password="$(< /dev/urandom tr -dc _A-Z-a-z-0-9 | head -c${1:-32};echo;)" \
        --from-literal=password="$(< /dev/urandom tr -dc _A-Z-a-z-0-9 | head -c${1:-32};echo;)" --dry-run -o yaml > mariadb-secret.yaml
```

2. Encrypt the generated secrets using kubeseal for enhanced security. Also, create the kustomization.yaml file, ensuring removal of plain text Kubernetes secret resources.
```bash
bash ../../../tools/kubeseal_secret.sh . ../../../tools/sealed-secret-tls.crt
# kustomize create --autodetect --recursive --namespace openstack .
```
**Note:** Make sure you remove plain text Kubernetes secret resources from `kustomization.yaml`
```bash
cat kustomization.yaml
```
3. Push the changes to your git repository

4. Apply the ArgoCD application to deploy MariaDB Cluster.
```bash
kubectl apply -f osh/argoCD/02-mariadb-argo.yaml
```

---

## Validation:
```bash
kubectl --namespace openstack get mariadbs
```

ArgoCD continuously monitors the configured Git repository for changes and automatically applies them to the Kubernetes cluster. Once the changes are pushed to the repository, ArgoCD will detect the update and synchronize with the latest version.

Check the ArgoCD UI to track the synchronization progress and ensure that the modifications are successfully applied to the cluster.