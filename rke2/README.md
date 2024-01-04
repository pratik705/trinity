# RKE2 Ansible Deployment

This repository can be used to deploy [Rancher RKE2](https://docs.rke2.io/) Kubernetes clusters on bare metal or virtual machines. It utilizes the [lablabs/ansible-role-rke2](https://github.com/lablabs/ansible-role-rke2) Ansible role for the installation.

---

## Prerequisites

Before getting started, ensure the following prerequisites are met:

- Clone this repository and navigate to the RKE2 directory:
```bash
git clone --recurse-submodules https://github.com/pratik705/trinity.git
cd trinity/rke2
```
Note: The `--recurse-submodules` option is used to clone the repository along with its submodules. This is necessary as the RKE2 deployment relies on an Ansible role and kube-ovn CNI (if used) submodule.

1. Configure passwordless SSH access from the machine where you'll run the Ansible playbook to the target nodes.
2. Update the `inventory.ini` file with details of the target nodes.
3. Customize the `site.yaml` file with the necessary Ansible variables. Refer to the [role variables documentation](https://github.com/lablabs/ansible-role-rke2?tab=readme-ov-file#role-variables) for more information.

---

## Installation

- Make sure all nodes can be reached using Ansible:
```bash
ansible -i inventory.ini -m ping all
```

- Execute the following command to deploy the RKE2 Kubernetes cluster:
```bash
ansible-playbook site.yaml -i inventory.ini
```

---

## Validation

After successful installation, validate the cluster by copying the RKE2 configuration file to your local Kubernetes configuration:
```bash
cp /tmp/rke2.yaml ~/.kube/config
kubectl get nodes
NAME                       STATUS   ROLES                       AGE     VERSION
controller01   Ready    control-plane,etcd,master   4d18h   v1.26.11+rke2r1
controller02   Ready    control-plane,etcd,master   4d18h   v1.26.11+rke2r1
controller03   Ready    control-plane,etcd,master   4d18h   v1.26.11+rke2r1
compute02      Ready    <none>                      29h     v1.26.11+rke2r1
compute03      Ready    <none>                      29h     v1.26.11+rke2r1
ceph-cap01     Ready    <none>                      4d18h   v1.26.11+rke2r1
ceph-cap02     Ready    <none>                      4d18h   v1.26.11+rke2r1
ceph-cap03     Ready    <none>                      4d18h   v1.26.11+rke2r1
```
**Note:**
- Depending on the CNI selected, additional steps may be required to ensure Kubernetes is in a working state.
- If using the `kube-ovn` CNI, follow the instructions in the next section.

---

# kube-ovn CNI

To use kube-ovn as the CNI, follow these steps:

1. Set the Ansible variable(`site.yaml`):
```bash
rke2_cni: none
```

2. Install the Ansible playbook:
```bash
ansible-playbook site.yaml -i inventory.ini
```

3. After the playbook completion, nodes will be in `NotReady` state due to the missing CNI.
```bash
# kubectl  get nodes
NAME                       STATUS     ROLES                       AGE     VERSION           
controller01   NotReady   control-plane,etcd,master   4h39m   v1.26.11+rke2r1
controller02   NotReady   control-plane,etcd,master   4h37m   v1.26.11+rke2r1
controller03   NotReady   control-plane,etcd,master   4h37m   v1.26.11+rke2r1
compute02      NotReady    <none>                      11h   v1.26.11+rke2r1
compute03      NotReady    <none>                      11h   v1.26.11+rke2r1
ceph-cap01     NotReady    <none>                      11h   v1.26.11+rke2r1
ceph-cap02     NotReady    <none>                      11h   v1.26.11+rke2r1
ceph-cap03     NotReady    <none>                      11h   v1.26.11+rke2r1
```

4. Install kube-ovn CNI using the provided [helm chart](https://github.com/kubeovn/kube-ovn/tree/master/charts).
5. Update charts/values.yaml based on your requirements.
```bash
git diff --unified=0  charts/values.yaml
diff --git a/charts/values.yaml b/charts/values.yaml
index 69f07c4b..83dfcab1 100644
--- a/charts/values.yaml
+++ b/charts/values.yaml
@@ -22 +22 @@ replicaCount: 1
-MASTER_NODES: ""
+MASTER_NODES: "xx.xx.xx.xx,xx.xx.xx.xx,xx.xx.xx.xx"
@@ -73,3 +73,3 @@ ipv4:
-  POD_CIDR: "10.16.0.0/16"
-  POD_GATEWAY: "10.16.0.1"
-  SVC_CIDR: "10.96.0.0/12"
+  POD_CIDR: "10.42.0.0/16"
+  POD_GATEWAY: "10.42.0.1"
+  SVC_CIDR: "10.43.0.0/16"

helm upgrade --install --debug kubeovn ./kube-ovn/charts --set replicaCount=3 -n kube-system
```

6. Validate the cluster:
```bash
kubectl  get nodes
NAME                       STATUS   ROLES                       AGE     VERSION
controller01   Ready    control-plane,etcd,master   8h      v1.26.11+rke2r1
controller02   Ready    control-plane,etcd,master   8h      v1.26.11+rke2r1
controller03   Ready    control-plane,etcd,master   8h      v1.26.11+rke2r1
compute02      Ready    <none>                      106s    v1.26.11+rke2r1
compute03      Ready    <none>                      2m1s    v1.26.11+rke2r1
ceph-cap01     Ready    <none>                      2m19s   v1.26.11+rke2r1
ceph-cap02     Ready    <none>                      4m9s    v1.26.11+rke2r1
ceph-cap03     Ready    <none>                      2m34s   v1.26.11+rke2r1

kubectl  get pods -n kube-system |egrep -i ovn
kube-ovn-cni-78g4x                                      1/1     Running     0             28h
kube-ovn-cni-dwqk6                                      1/1     Running     1 (28h ago)   28h
kube-ovn-cni-jqztb                                      1/1     Running     2 (27h ago)   28h
kube-ovn-cni-mhz76                                      1/1     Running     1 (14h ago)   28h
kube-ovn-cni-n7xjl                                      1/1     Running     2 (28h ago)   28h
kube-ovn-cni-r94cp                                      1/1     Running     0             28h
kube-ovn-cni-r9srv                                      1/1     Running     2 (28h ago)   28h
kube-ovn-cni-s6nf9                                      1/1     Running     2 (28h ago)   28h
kube-ovn-controller-798cdfc7bd-bzm2m                    1/1     Running     0             28h
kube-ovn-controller-798cdfc7bd-g5gkp                    1/1     Running     0             14h
kube-ovn-controller-798cdfc7bd-qf9zr                    1/1     Running     0             27h
kube-ovn-monitor-7864f4dc66-mq6h9                       1/1     Running     0             27h
kube-ovn-pinger-cbwhz                                   1/1     Running     0             28h
kube-ovn-pinger-ct7mf                                   1/1     Running     0             28h
kube-ovn-pinger-glnsz                                   1/1     Running     0             28h
kube-ovn-pinger-kc6mh                                   1/1     Running     1 (14h ago)   28h
kube-ovn-pinger-lnbsf                                   1/1     Running     1 (28h ago)   28h
kube-ovn-pinger-rzgp6                                   1/1     Running     0             28h
kube-ovn-pinger-vx6qj                                   1/1     Running     1 (27h ago)   28h
kube-ovn-pinger-wjg28                                   1/1     Running     0             28h
ovn-central-74c9cc96d5-gqqqw                            1/1     Running     1 (27h ago)   27h
ovn-central-74c9cc96d5-nrhhl                            1/1     Running     0             28h
ovn-central-74c9cc96d5-qthlx                            1/1     Running     0             28h
ovs-ovn-b9jpw                                           1/1     Running     0             28h
ovs-ovn-czzrc                                           1/1     Running     1 (28h ago)   28h
ovs-ovn-dl22v                                           1/1     Running     1 (14h ago)   28h
ovs-ovn-nnbwk                                           1/1     Running     0             28h
ovs-ovn-q5n9r                                           1/1     Running     1 (28h ago)   28h
ovs-ovn-rdfmf                                           1/1     Running     1 (28h ago)   28h
ovs-ovn-tk5ml                                           1/1     Running     0             28h
ovs-ovn-zx68s                                           1/1     Running     1 (27h ago)   28h
```

---

# Upgrade the RKE2 cluster

To upgrade the RKE2 cluster, follow these steps:
1. Define the `rke2_version` Ansible variable in the `site.yaml` file. You can choose the desired version from the [RKE2 releases](https://github.com/rancher/rke2/releases).

In order to upgrade the RKE2 cluster, define the `rke2_version` ansible variable and re-run the ansible playbook. The available versions can be found [here](https://github.com/rancher/rke2/releases)
```yaml
cat site.yaml
[...]
    rke2_version: v1.26.11+rke2r1
[...]  
```

2. Re-run the Ansible playbook:
```bash
ansible-playbook site.yaml -i inventory.ini
```
This will initiate the upgrade process with the specified RKE2 version.


