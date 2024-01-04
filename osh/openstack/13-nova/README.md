# Nova

This guide provides instructions to deploy OpenStack Nova on a Kubernetes cluster. 

**Note:** You can use the manifests from this repository as an example and update the details according to your requirements.

**Note:** 
- We will use the CEPH rbd pool `cinder.volumes.gold` and rbd client `rbd-client` created while deploying `CEPH`.
- `rbd-client1` Kubernetes secret is already created while deploying Cinder.
- `ceph-etc` Kubernetes configmap is already created while deploying Cinder
  
1. Update CEPH rbd details in `values.yaml`:
```bash
# cat values.yaml
[...]
ceph_client:
  configmap: ceph-etc
  user_secret_name: rbd-client1
  [...]
  ceph:
    enabled: true
    admin_keyring: null
    cinder:
      user: "rbd-client"
      keyring: <`kubectl get secret rook-ceph-client-rbd-client -o jsonpath='{.data.rbd-client}' -n rook-ceph |base64 -d`>
      secret_uuid: 457eb676-33da-42ec-9a8c-9293d545c337  
    [...]
    libvirt:
      connection_uri: "qemu+unix:///system?socket=/run/libvirt/libvirt-sock"
      images_type: rbd
      images_rbd_pool: cinder.volumes.gold
      images_rbd_ceph_conf: /etc/ceph/ceph.conf
      rbd_user: rbd-client
      rbd_secret_uuid: 457eb676-33da-42ec-9a8c-9293d545c337
      disk_cachemodes: "network=writeback"
      hw_disk_discard: unmap  
[...]
```
2. Generate the manifests using helm template:
```bash
helm template nova ../../openstack-helm/nova \
    -f values.yaml \
    --set endpoints.identity.auth.admin.password="$(kubectl --namespace openstack get secret keystone-admin -o jsonpath='{.data.password}' | base64 -d)" \
    --set endpoints.identity.auth.nova.password="$(kubectl --namespace openstack get secret nova-admin -o jsonpath='{.data.password}' | base64 -d)" \
    --set endpoints.identity.auth.neutron.password="$(kubectl --namespace openstack get secret neutron-admin -o jsonpath='{.data.password}' | base64 -d)" \
    --set endpoints.identity.auth.ironic.password="$(kubectl --namespace openstack get secret ironic-admin -o jsonpath='{.data.password}' | base64 -d)" \
    --set endpoints.identity.auth.placement.password="$(kubectl --namespace openstack get secret placement-admin -o jsonpath='{.data.password}' | base64 -d)" \
    --set endpoints.identity.auth.cinder.password="$(kubectl --namespace openstack get secret cinder-admin -o jsonpath='{.data.password}' | base64 -d)" \
    --set endpoints.oslo_db.auth.admin.password="$(kubectl --namespace openstack get secret mariadb -o jsonpath='{.data.root-password}' | base64 -d)" \
    --set endpoints.oslo_db.auth.nova.password="$(kubectl --namespace openstack get secret nova-db-password -o jsonpath='{.data.password}' | base64 -d)" \
    --set endpoints.oslo_db_api.auth.admin.password="$(kubectl --namespace openstack get secret mariadb -o jsonpath='{.data.root-password}' | base64 -d)" \
    --set endpoints.oslo_db_api.auth.nova.password="$(kubectl --namespace openstack get secret nova-db-password -o jsonpath='{.data.password}' | base64 -d)" \
    --set endpoints.oslo_db_cell0.auth.admin.password="$(kubectl --namespace openstack get secret mariadb -o jsonpath='{.data.root-password}' | base64 -d)" \
    --set endpoints.oslo_db_cell0.auth.nova.password="$(kubectl --namespace openstack get secret nova-db-password -o jsonpath='{.data.password}' | base64 -d)" \
    --set endpoints.oslo_messaging.auth.admin.password="$(kubectl --namespace openstack get secret rabbitmq-default-user -o jsonpath='{.data.password}' | base64 -d)" \
    --set endpoints.oslo_messaging.auth.nova.password="$(kubectl --namespace openstack get secret nova-rabbitmq-password -o jsonpath='{.data.password}' | base64 -d)" \
    -n openstack \
    --output-dir manifests
```

3. Extract the Kubernetes secret resource from the manifest files:
```bash
python3 ../../../tools/extract_secrets.py  manifests/
```

4. Encrypt the secrets using kubeseal:
```bash
bash ../../../tools/kubeseal_secret.sh  manifests/ ../../../tools/sealed-secret-tls.crt
```

5. Create the final `kustomization.yaml`:
**Note:** Make sure you remove plain text Kubernetes secret resources from `kustomization.yaml`.
```bash
cat kustomization.yaml
```

6. Commit and push the changes to your Git repository.

7. Apply the ArgoCD application to deploy Keystone.
```bash
kubectl  apply -f osh/argoCD/13-nova-argo.yaml
```

---

## Validation:
```bash
kubectl get pods -n openstack |egrep -i nova
kubectl exec -it openstack-admin-client -n openstack -- openstack catalog list
kubectl exec -it openstack-admin-client -n openstack -- openstack service list
kubectl exec -it openstack-admin-client -n openstack -- openstack compute service list
```

ArgoCD continuously monitors the configured Git repository for changes and automatically applies them to the Kubernetes cluster. Once the changes are pushed to the repository, ArgoCD will detect the update and synchronize with the latest version.

Check the ArgoCD UI to track the synchronization progress and ensure that the modifications are successfully applied to the cluster.