# Cinder

This guide provides instructions to deploy OpenStack Cinder on a Kubernetes cluster. 

**Note:** You can use the manifests from this repository as an example and update the details according to your requirements.

1. Generate the necessary secrets for OpenStack Cinder, ensuring secure and randomized passwords.
```bash
mkdir secrets
cd secrets
kubectl --namespace openstack \
        create secret generic cinder-rabbitmq-password \
        --type Opaque \
        --from-literal=username="cinder" \
        --from-literal=password="$(< /dev/urandom tr -dc _A-Z-a-z-0-9 | head -c${1:-64};echo;)"  \
        --dry-run -o yaml > cinder-rabbitmq-password-secret.yaml
kubectl --namespace openstack \
        create secret generic cinder-db-password \
        --type Opaque \
        --from-literal=password="$(< /dev/urandom tr -dc _A-Z-a-z-0-9 | head -c${1:-32};echo;)"  \
        --dry-run -o yaml > cinder-db-password-secret.yaml
kubectl --namespace openstack \
        create secret generic cinder-admin \
        --type Opaque \
        --from-literal=password="$(< /dev/urandom tr -dc _A-Z-a-z-0-9 | head -c${1:-32};echo;)"  \
        --dry-run -o yaml > cinder-admin-secret.yaml
```

2. Encrypt the generated secrets using kubeseal for enhanced security. Also, create the kustomization.yaml file, ensuring removal of plain text Kubernetes secret resources.
```bash
bash ../../../../tools/kubeseal_secret.sh . ../../../../tools/sealed-secret-tls.crt
kustomize create --autodetect --recursive --namespace openstack .
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
helm template cinder ../../openstack-helm/cinder \
    -f values.yaml \
    --set endpoints.identity.auth.admin.password="$(kubectl --namespace openstack get secret keystone-admin -o jsonpath='{.data.password}' | base64 -d)" \
    --set endpoints.identity.auth.cinder.password="$(kubectl --namespace openstack get secret cinder-admin -o jsonpath='{.data.password}' | base64 -d)" \
    --set endpoints.oslo_db.auth.admin.password="$(kubectl --namespace openstack get secret mariadb -o jsonpath='{.data.root-password}' | base64 -d)" \
    --set endpoints.oslo_db.auth.cinder.password="$(kubectl --namespace openstack get secret cinder-db-password -o jsonpath='{.data.password}' | base64 -d)" \
    --set endpoints.oslo_messaging.auth.admin.password="$(kubectl --namespace openstack get secret rabbitmq-default-user -o jsonpath='{.data.password}' | base64 -d)" \
    --set endpoints.oslo_messaging.auth.cinder.password="$(kubectl --namespace openstack get secret cinder-rabbitmq-password -o jsonpath='{.data.password}' | base64 -d)" \
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
**Note:**
- It will use the CEPH rbd pool `cinder.volumes.gold` and rbd client `rbd-client` created while deploying `CEPH`.

7. Fetch rbd client key which will be used in the next step:
```bash
kubectl get secret rook-ceph-client-rbd-client -o jsonpath='{.data.rbd-client}' -n rook-ceph |base64 -d
```

8. Create a new secret which will be used by Cinder to access the data from the rbd pool:
```bash
apiVersion: v1
stringData:
  key: <rbd_client_key>
kind: Secret
metadata:
  name: rbd-client1
  namespace: openstack
type: kubernetes.io/rook
```

9. Encrypt the secret using kubeseal:
```bash
bash ../../../tools/kubeseal_secret.sh  addon_manifests/ ../../../tools/sealed-secret-tls.crt
```

10. Fetch CEPH MON svc IP's and update `addon_manifests/ceph-etc-CM.yaml`
```bash
kubectl get svc -n rook-ceph |egrep -i ceph-mon | awk '{print $3}'

# cat addon_manifests/ceph-etc-CM.yaml
apiVersion: v1
data:
  ceph.conf: |
    [global]
    cephx = true
    cephx_cluster_require_signatures = true
    cephx_require_signatures = false
    cephx_service_require_signatures = false
    debug_ms = 0/0
    log_file = /dev/stdout
    mon_cluster_log_file = /dev/stdout
    mon_host = [v2:<mon1_svc_ip>:3300/0,v1:<mon1_svc_ip>:6789/0],[v2:<mon2_svc_ip>:3300/0,v1:<mon2_svc_ip>:6789/0],[v2:<mon3_svc_ip>:3300/0,v1:<mon3_svc_ip>:6789/0]
    objecter_inflight_op_bytes = 1073741824
    objecter_inflight_ops = 10240
kind: ConfigMap
metadata:
  name: ceph-etc
  namespace: openstack
```

10.  Create the final `kustomization.yaml`, removing any duplicate secrets already applied in Step 2.
**Note:** Make sure you remove plain text Kubernetes secret resources from `kustomization.yaml`
```bash
cat kustomization.yaml
```

11. Commit and push the changes to your Git repository.

12. Apply the ArgoCD application to deploy Keystone.
```bash
kubectl  apply -f osh/argoCD/09-cinder-argo.yaml
```

---

## Validation:
```bash
kubectl get pods -n openstack |egrep -i cinder
kubectl exec -it openstack-admin-client -n openstack -- openstack catalog list
kubectl exec -it openstack-admin-client -n openstack -- openstack service list
kubectl  exec -it openstack-admin-client -n openstack -- openstack volume service list
```

ArgoCD continuously monitors the configured Git repository for changes and automatically applies them to the Kubernetes cluster. Once the changes are pushed to the repository, ArgoCD will detect the update and synchronize with the latest version.

Check the ArgoCD UI to track the synchronization progress and ensure that the modifications are successfully applied to the cluster.