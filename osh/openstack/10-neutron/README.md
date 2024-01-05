# Neutron

This guide provides instructions to deploy OpenStack Neutron on a Kubernetes cluster. 

**Note:** You can use the manifests from this repository as an example and update the details according to your requirements.

1. Generate the necessary secrets for OpenStack Neutron and dependent services, ensuring secure and randomized passwords.
```bash
mkdir -p pre-req/secrets/{nova,designate,ironic,neutron,placement}

cd pre-req/
# Placement
kubectl --namespace openstack \
        create secret generic placement-db-password \
        --type Opaque \
        --from-literal=password="$(< /dev/urandom tr -dc _A-Z-a-z-0-9 | head -c${1:-32};echo;)" \
        --dry-run -o yaml > secrets/placement/placement-db-password-secret.yaml
kubectl --namespace openstack \
        create secret generic placement-admin \
        --type Opaque \
        --from-literal=password="$(< /dev/urandom tr -dc _A-Z-a-z-0-9 | head -c${1:-32};echo;)" \
        --dry-run -o yaml > secrets/placement/placement-admin-secret.yaml

# Nova:
kubectl --namespace openstack \
        create secret generic nova-db-password \
        --type Opaque \
        --from-literal=password="$(< /dev/urandom tr -dc _A-Z-a-z-0-9 | head -c${1:-32};echo;)" \
        --dry-run -o yaml > secrets/nova/nova-db-password-secret.yaml
kubectl --namespace openstack \
        create secret generic nova-admin \
        --type Opaque \
        --from-literal=password="$(< /dev/urandom tr -dc _A-Z-a-z-0-9 | head -c${1:-32};echo;)" \
        --dry-run -o yaml > secrets/nova/nova-admin-secret.yaml
kubectl --namespace openstack \
        create secret generic nova-rabbitmq-password \
        --type Opaque \
        --from-literal=username="nova" \
        --from-literal=password="$(< /dev/urandom tr -dc _A-Z-a-z-0-9 | head -c${1:-64};echo;)" \
        --dry-run -o yaml > secrets/nova/nova-rabbitmq-secret.yaml

# Ironic:
kubectl --namespace openstack \
        create secret generic ironic-admin \
        --type Opaque \
        --from-literal=password="$(< /dev/urandom tr -dc _A-Z-a-z-0-9 | head -c${1:-32};echo;)" \
        --dry-run -o yaml > secrets/ironic/ironic-admin-secret.yaml

# Designate:
kubectl --namespace openstack \
        create secret generic designate-admin \
        --type Opaque \
        --from-literal=password="$(< /dev/urandom tr -dc _A-Z-a-z-0-9 | head -c${1:-32};echo;)" \
        --dry-run -o yaml > secrets/designate/designate-admin-secret.yaml

# Neutron
kubectl --namespace openstack \
        create secret generic neutron-rabbitmq-password \
        --type Opaque \
        --from-literal=username="neutron" \
        --from-literal=password="$(< /dev/urandom tr -dc _A-Z-a-z-0-9 | head -c${1:-64};echo;)" \
        --dry-run -o yaml > secrets/neutron/neutron-rabbitmq-password-secret.yaml
kubectl --namespace openstack \
        create secret generic neutron-db-password \
        --type Opaque \
        --from-literal=password="$(< /dev/urandom tr -dc _A-Z-a-z-0-9 | head -c${1:-32};echo;)" \
        --dry-run -o yaml > secrets/neutron/neutron-db-password-secret.yaml
kubectl --namespace openstack \
        create secret generic neutron-admin \
        --type Opaque \
        --from-literal=password="$(< /dev/urandom tr -dc _A-Z-a-z-0-9 | head -c${1:-32};echo;)" \
        --dry-run -o yaml > secrets/neutron/neutron-admin-secret.yaml
```

2. Encrypt the generated secrets using kubeseal for enhanced security. Also, create the kustomization.yaml file, ensuring removal of plain text Kubernetes secret resources.
```bash
bash ../../../../tools/kubeseal_secret.sh secrets/ ../../../../tools/sealed-secret-tls.crt
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
helm template neutron ../../openstack-helm/neutron \
    -f values.yaml \
    --set endpoints.identity.auth.admin.password="$(kubectl --namespace openstack get secret keystone-admin -o jsonpath='{.data.password}' | base64 -d)" \
    --set endpoints.identity.auth.neutron.password="$(kubectl --namespace openstack get secret neutron-admin -o jsonpath='{.data.password}' | base64 -d)" \
    --set endpoints.identity.auth.nova.password="$(kubectl --namespace openstack get secret nova-admin -o jsonpath='{.data.password}' | base64 -d)" \
    --set endpoints.identity.auth.placement.password="$(kubectl --namespace openstack get secret placement-admin -o jsonpath='{.data.password}' | base64 -d)" \
    --set endpoints.identity.auth.designate.password="$(kubectl --namespace openstack get secret designate-admin -o jsonpath='{.data.password}' | base64 -d)" \
    --set endpoints.identity.auth.ironic.password="$(kubectl --namespace openstack get secret ironic-admin -o jsonpath='{.data.password}' | base64 -d)" \
    --set endpoints.oslo_db.auth.admin.password="$(kubectl --namespace openstack get secret mariadb -o jsonpath='{.data.root-password}' | base64 -d)" \
    --set endpoints.oslo_db.auth.neutron.password="$(kubectl --namespace openstack get secret neutron-db-password -o jsonpath='{.data.password}' | base64 -d)" \
    --set endpoints.oslo_messaging.auth.admin.password="$(kubectl --namespace openstack get secret rabbitmq-default-user -o jsonpath='{.data.password}' | base64 -d)" \
    --set endpoints.oslo_messaging.auth.neutron.password="$(kubectl --namespace openstack get secret neutron-rabbitmq-password -o jsonpath='{.data.password}' | base64 -d)" \
    --set conf.neutron.ovn.ovn_nb_connection="tcp:$(kubectl get service ovn-nb -o jsonpath='{.spec.clusterIP}:{.spec.ports[0].port}' -n kube-system)" \
    --set conf.neutron.ovn.ovn_sb_connection="tcp:$(kubectl get service ovn-sb -o jsonpath='{.spec.clusterIP}:{.spec.ports[0].port}' -n kube-system)" \
    --set conf.plugins.ml2_conf.ovn.ovn_nb_connection="tcp:$(kubectl get service ovn-nb -o jsonpath='{.spec.clusterIP}:{.spec.ports[0].port}' -n kube-system)" \
    --set conf.plugins.ml2_conf.ovn.ovn_sb_connection="tcp:$(kubectl get service ovn-sb -o jsonpath='{.spec.clusterIP}:{.spec.ports[0].port}' -n kube-system)" \
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


9. Configure OVN for OpenStack

- Set the name of the OVS integration bridge we'll use. In general, this should be br-int.
```bash
kubectl annotate nodes $(kubectl get nodes -l 'openstack-network-node=enabled' -o 'jsonpath={.items[*].metadata.name}') ovn.openstack.org/int_bridge='br-int'
```

- Set the name of the OVS bridges we'll use. These are the bridges you will use on your hosts.

NOTE The functional example here annotates all nodes; however, not all nodes have to have the same setup.
```bash
kubectl annotate nodes $(kubectl get nodes -l 'openstack-network-node=enabled' -o 'jsonpath={.items[*].metadata.name}') ovn.openstack.org/bridges='br-ex'
```

- Set the bridge mapping. These are colon delimitated between OVS_BRIDGE:PHYSICAL_INTERFACE_NAME. Multiple bridge mappings can be defined here and are separated by commas.
```bash
kubectl annotate nodes $(kubectl get nodes -l 'openstack-network-node=enabled' -o 'jsonpath={.items[*].metadata.name}') ovn.openstack.org/ports='br-ex:bond0'
```

- Set the OVN bridge mapping. This maps the Neutron interfaces to the ovs bridge names. These are colon delimitated between OVS_BRIDGE:PHYSICAL_INTERFACE_NAME. Multiple bridge mappings can be defined here and are separated by commas.
```bash
kubectl annotate nodes $(kubectl get nodes -l 'openstack-network-node=enabled' -o 'jsonpath={.items[*].metadata.name}') ovn.openstack.org/mappings='physnet1:br-ex'
```

- Set the OVN availability zones. Multiple network availability zones can be defined and are colon separated.
```bash
kubectl annotate nodes $(kubectl get nodes -l 'openstack-network-node=enabled' -o 'jsonpath={.items[*].metadata.name}') ovn.openstack.org/availability_zones='nova'
```
Note the "nova" availability zone is an assumed default.

- Set the OVN gateway nodes.
```bash
kubectl annotate nodes $(kubectl get nodes -l 'openstack-network-node=enabled' -o 'jsonpath={.items[*].metadata.name}') ovn.openstack.org/gateway='enabled'
```
Note while all compute nodes could be a gateway, not all nodes should be a gateway.


10. Apply the ArgoCD application to deploy Keystone.
```bash
kubectl  apply -f osh/argoCD/10-neutron-argo.yaml
```

11. Confirm if all the neutron pods are UP:
```bash
kubectl get pods -n openstack |egrep -i neutron
```

---

## Validation:
```bash
kubectl get pods -n openstack |egrep -i neutron
# NOTE: `neutron-ovn-metadata-agent` will not be ready as it expects nova endpoint.
kubectl exec -it openstack-admin-client -n openstack -- openstack catalog list
kubectl exec -it openstack-admin-client -n openstack -- openstack service list
kubectl exec -it openstack-admin-client -n openstack -- openstack network agent list
```

ArgoCD continuously monitors the configured Git repository for changes and automatically applies them to the Kubernetes cluster. Once the changes are pushed to the repository, ArgoCD will detect the update and synchronize with the latest version.

Check the ArgoCD UI to track the synchronization progress and ensure that the modifications are successfully applied to the cluster.