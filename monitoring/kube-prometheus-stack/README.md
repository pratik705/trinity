# kube-prometheus-stack

kube-prometheus-stack deploys Prometheus, Grafana and Alertmanager to offer seamless observability for Kubernetes clusters. It includes pre-configured dashboards and alerting, simplifying monitoring setup for resource usage, performance, and health metrics. 

## Pre-installation Checks:
Before proceeding with the kube-prometheus-stack installation, ensure the following prerequisites::
- `managed-services` are installed
- `ceph-rook` is deployed
- ArgoCD is up and running as expected. 
- Git repository is connected to the ArgoCD. Refer to [\[1\]](https://argo-cd.readthedocs.io/en/stable/user-guide/private-repositories/)[\[2\]](https://argo-cd.readthedocs.io/en/latest/user-guide/commands/argocd_repo_add/)
  
## Installation:
To install kube-prometheus-stack according as per your requirement, navigate to the kube-prometheus-stack directory, make the necessary modifications to Kubernetes manifest/values.yaml, and deploy it using ArgoCD. You can kickstart your setup by copying the provided examples from this repository.

**Note:** You can use the manifests from this repository as an example and update the details according to your requirements.

- Clone this repository and navigate to the `monitoring/kube-prometheus-stack` directory:
```bash
git clone --recurse-submodules https://github.com/pratik705/trinity.git
cd trinity/monitoring/kube-prometheus-stack
```
Note: The `--recurse-submodules` option is used to clone the repository along with its submodules.
- Once you have made your changes, commit and push them to your Git repository.
```bash
git add .
git commit -m "Describe your changes"
git push origin main
```

- Once the changes are pushed to Git repository, use ArgoCD for deployment:
```bash
kubectl apply -f monitoring/argoCD/kube-prometheus-stack-argo.yaml
```

--- 

## Validation:
```bash
kubectl get prometheus -n rackspace-system
kubectl get alertmanagers -n rackspace-system
kubectl get pvc -n rackspace-system
```
- Access the Grafana/alertmanager/prometheus URL's
  
ArgoCD continuously monitors the configured Git repository for changes and automatically applies them to the Kubernetes cluster. Once the changes are pushed to the repository, ArgoCD will detect the update and synchronize with the latest version.

Check the ArgoCD UI to track the synchronization progress and ensure that the modifications are successfully applied to the cluster.