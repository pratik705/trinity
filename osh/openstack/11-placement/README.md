# Placement

This guide provides instructions to deploy OpenStack Placement on a Kubernetes cluster. 

**Note:** You can use the manifests from this repository as an example and update the details according to your requirements.

1. Generate the manifests using helm template:
```bash
helm template placement ../../openstack-helm/placement \
    -f values.yaml \
    --set endpoints.identity.auth.admin.password="$(kubectl --namespace openstack get secret keystone-admin -o jsonpath='{.data.password}' | base64 -d)" \
    --set endpoints.identity.auth.placement.password="$(kubectl --namespace openstack get secret placement-admin -o jsonpath='{.data.password}' | base64 -d)" \
    --set endpoints.oslo_db.auth.admin.password="$(kubectl --namespace openstack get secret mariadb -o jsonpath='{.data.root-password}' | base64 -d)" \
    --set endpoints.oslo_db.auth.placement.password="$(kubectl --namespace openstack get secret placement-db-password -o jsonpath='{.data.password}' | base64 -d)" \
    --set endpoints.oslo_db.auth.nova_api.password="$(kubectl --namespace openstack get secret nova-db-password -o jsonpath='{.data.password}' | base64 -d)" \
    -n openstack \
    --output-dir manifests
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
kubectl  apply -f osh/argoCD/11-placement-argo.yaml
```

---

## Validation:
```bash
kubectl get pods -n openstack |egrep -i placement
kubectl exec -it openstack-admin-client -n openstack -- openstack catalog list
kubectl exec -it openstack-admin-client -n openstack -- openstack service list
```

ArgoCD continuously monitors the configured Git repository for changes and automatically applies them to the Kubernetes cluster. Once the changes are pushed to the repository, ArgoCD will detect the update and synchronize with the latest version.

Check the ArgoCD UI to track the synchronization progress and ensure that the modifications are successfully applied to the cluster.