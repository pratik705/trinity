# Managed Services for OpenStack-Helm Deployment

This page serves as an introduction to the services required to prepare a fresh Kubernetes environment for deploying [OpenStack-Helm](https://github.com/openstack/openstack-helm).

## Included Services:

1. **Namespace:** A dedicated space where supporting services will be installed.
2. **Cert-Manager:** Manages the life cycle of certificates for consumption by the Kubernetes cluster.
3. **MetalLB:** Provides load balancer services for the environment.
4. **Sealed-secret:** Encrypts plain-text secrets, ensuring secure storage in a Git repository.
5. **Ingress-Nginx:** Deploys an Ingress Controller, facilitating the creation of Ingress resources.
6. **ArgoCD:** Enables the management of Kubernetes applications in a GitOps manner.

---

## Configuration Instructions:

To configure each service, navigate to the respective service directory and make the necessary changes before using Kustomize for installation. Instructions can be found in each service's directory. 

**Note:** You can use the manifests from this repository as an example and update the details according to your requirements.

Please proceed once the required parameters are updated for each service.

---

## Installation:

1. Validate the generated manifest files:
```bash
kubectl kustomize --enable-helm=true .
```

2. Install the managed-services:
```bash
sh ./install.sh
```

---

## Validation:
1. Ensure all pods and resources in the `rackspace-system` namespace are up.
```bash
kubectl get pods -n rackspace-system
kubectl get issuer -n rackspace-system
kubectl get cert -n rackspace-system
```

2. Access the ArgoCD Ingress resource.
```bash
kubectl get ingress -n rackspace-system
curl -Ik https://argocd.pbandark.com
```

---

## Managing the Installed managed-services using ArgoCD:
1. Access ArgoCD using the FQDN.
2. Retrieve the admin password from the Kubernetes secret:
```bash
kubectl get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' -n rackspace-system |base64 -d
```
3. Login to the ArgoCD UI
4. Add the Git repository to manage/deploy Kubernetes applications. Refer to [\[1\]](https://argo-cd.readthedocs.io/en/stable/user-guide/private-repositories/)[\[2\]](https://argo-cd.readthedocs.io/en/latest/user-guide/commands/argocd_repo_add/)
5. Once the Git repository is active in ArgoCD, apply the managed-services ArgoCD manifest:
```bash
kubectl apply -f managed-services-argo.yaml
```

6. Once sealed-secret is deployed, you can save sealed secret certificates, which will be used to encrypt Kubernetes secret resources when deploying openstack-helm.
```bash
kubectl get secret sealed-secrets-<xxxx>  -o jsonpath="{['data']['tls\.key']}"  -n rackspace-system | base64 -d > ../tools/sealed-secret-tls.key

kubeseal --controller-namespace rackspace-system  --controller-name sealed-secrets --fetch-cert > ../tools/sealed-secret-tls.crt
```
**Note:** Make sure to take a backup of sealed-secret-tls.key and sealed-secret-tls.crt.

---

## Modifying Managed Services:

1. Make the required changes to the managed-service in your local development environment.
2. Commit and push the changes to your Git repository.
```bash
git add .
git commit -m "Describe your changes"
git push origin main
```

---

- All managed services will now appear in the ArgoCD UI.
![managed_services](../screenshots/managed_services_argocd.jpg?raw=true)

ArgoCD continuously monitors the configured Git repository for changes and automatically applies them to the Kubernetes cluster. Once the changes are pushed to the repository, ArgoCD will detect the update and synchronize with the latest version.

Check the ArgoCD UI to track the synchronization progress and ensure that the modifications are successfully applied to the cluster.