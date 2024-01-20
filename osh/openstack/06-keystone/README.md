# Keystone

This guide provides instructions to deploy OpenStack Keystone on a Kubernetes cluster. Keystone is a critical component of the OpenStack identity service.

**Note:** You can use the manifests from this repository as an example and update the details according to your requirements.

1. Generate the necessary secrets for OpenStack Keystone, ensuring secure and randomized passwords.
```bash
mkdir secrets
cd secrets
kubectl --namespace openstack \
        create secret generic keystone-rabbitmq-password \
        --type Opaque \
        --from-literal=username="keystone" \
        --from-literal=password="$(< /dev/urandom tr -dc _A-Z-a-z-0-9 | head -c${1:-64};echo;)" \
        --dry-run -o yaml > keystone-rabbitmq-password-secret.yaml
kubectl --namespace openstack \
        create secret generic keystone-db-password \
        --type Opaque \
        --from-literal=password="$(< /dev/urandom tr -dc _A-Z-a-z-0-9 | head -c${1:-32};echo;)" \
        --dry-run -o yaml > keystone-db-password-secret.yaml
kubectl --namespace openstack \
        create secret generic keystone-admin \
        --type Opaque \
        --from-literal=password="$(< /dev/urandom tr -dc _A-Z-a-z-0-9 | head -c${1:-32};echo;)" \
        --dry-run -o yaml > keystone-admin-secret.yaml
kubectl --namespace openstack \
        create secret generic keystone-credential-keys \
        --type Opaque \
        --from-literal=password="$(< /dev/urandom tr -dc _A-Z-a-z-0-9 | head -c${1:-32};echo;)" \
        --dry-run -o yaml > keystone-credential-keys-secret.yaml
```

2. Encrypt the generated secrets using kubeseal for enhanced security. Also, create the kustomization.yaml file, ensuring removal of plain text Kubernetes secret resources.
```bash
bash ../../../../tools/kubeseal_secret.sh . ../../../../tools/sealed-secret-tls.crt
# kustomize create --autodetect --recursive --namespace openstack .
```
**Note:** Make sure you remove plain text Kubernetes secret resources from `kustomization.yaml`
```bash
cat kustomization.yaml
```

3. Apply the encrypted secrets to the Kubernetes cluster.
```bash
kubectl  apply -k .
```

4. Generate the manifests using helm template:
```bash
cd ../
helm template keystone ../../openstack-helm/keystone/ \
-f values.yaml \
--set endpoints.identity.auth.admin.password="$(kubectl --namespace openstack get secret keystone-admin -o jsonpath='{.data.password}' | base64 -d)" \
--set endpoints.oslo_db.auth.admin.password="$(kubectl --namespace openstack get secret mariadb -o jsonpath='{.data.root-password}' | base64 -d)" \
--set endpoints.oslo_db.auth.keystone.password="$(kubectl --namespace openstack get secret keystone-db-password -o jsonpath='{.data.password}' | base64 -d)" \
--set endpoints.oslo_messaging.auth.admin.password="$(kubectl --namespace openstack get secret rabbitmq-default-user -o jsonpath='{.data.password}' | base64 -d)" \
--set endpoints.oslo_messaging.auth.keystone.password="$(kubectl --namespace openstack get secret keystone-rabbitmq-password -o jsonpath='{.data.password}' | base64 -d)" \
-n openstack \
--output-dir manifests
```

5. Extract the Kubernetes secret resource from the manifest files:
```bash
python3 ../../../tools/extract_secrets.py  manifests/
```

6. Encrypt the secrets using kubeseal:
```bash
bash ../../../tools/kubeseal_secret.sh  manifests/ ../../../tools/sealed-secret-tls.crt
```

7. Create the final `kustomization.yaml`, removing any duplicate secrets already applied in Step 2.
**Note:** Make sure you remove plain text Kubernetes secret resources from `kustomization.yaml`
```bash
cat kustomization.yaml
```

8. Commit and push the changes to your Git repository.

9. Apply the ArgoCD application to deploy Keystone.
```bash
kubectl  apply -f osh/argoCD/06-keystone-argo.yaml
```

---

## Validation:
```bash
kubectl get pods -n openstack |egrep -i keystone
kubectl exec -it openstack-admin-client -n openstack -- openstack catalog list
kubectl exec -it openstack-admin-client -n openstack -- openstack service list
```

ArgoCD continuously monitors the configured Git repository for changes and automatically applies them to the Kubernetes cluster. Once the changes are pushed to the repository, ArgoCD will detect the update and synchronize with the latest version.

Check the ArgoCD UI to track the synchronization progress and ensure that the modifications are successfully applied to the cluster.