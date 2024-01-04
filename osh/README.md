# OSH

OpenStack-Helm deploys OpenStack services on top of a Kubernetes Cluster. For additional details, please refer to the upstream project [link](https://wiki.openstack.org/wiki/Openstack-helm)

---

## Getting started
- Change to submodules directory and fetch the helm charts
```bash
cd osh/openstack-helm
make all

cd osh/openstack-helm-infra
make all
```

- Make sure all the Kubernetes nodes which will be part of OpenStack are correctly labeled. 
  - OpenStack Controllers:
    - openstack-control-plane=enabled
    - openvswitch=enabled
    - l3-agent=enabled
    - openstack-network-node=enabled

  - OpenStack Computes:
    - openstack-compute-node=enabled
    - openvswitch=enabled
    - l3-agent=enabled
    - openstack-network-node=enabled
---

## Installation
To start fresh, please proceed in the following order. If you already have an existing Kubernetes cluster and only want to install specific services, you can jump to the respective section.


### Deploy OpenStack namespace:
```bash
kubectl apply -f osh/argoCD/01-namespace-argo.yaml
```
---

### Deploy mariadb-operator and Mariadb Cluster:
#### Deploy mariadb-operator
```bash
kubectl apply -f osh/argoCD/02-mariadb-operator-argo.yaml
```

#### Deploy MariaDB Cluster
- Follow the detailed installation instructions [here](https://github.com/pratik705/trinity/blob/main/osh/openstack/02-mariadb/README.md).

---

### Deploy rabbitmq-operator and RabbitMQ Cluster:
#### Deploy rabbitmq-operator
```bash
kubectl apply -f osh/argoCD/03-rabbitmq-operator-argo.yaml
```

#### Deploy RabbitMQ Cluster
```bash
kubectl apply -f osh/argoCD/04-rabbitmq-cluster-argo.yaml
```

#### Validation:
```bash
kubectl --namespace openstack get rabbitmqclusters.rabbitmq.com
```
---

### Deploy Memcached:
#### Deploy Memcached Cluster
```
kubectl apply -f osh/argoCD/05-memcached-argo.yaml
```

#### Validation:
```bash
kubectl --namespace openstack get horizontalpodautoscaler.autoscaling memcached
```
---

### Deploy Keystone
- Follow the detailed installation instructions [here](https://github.com/pratik705/trinity/blob/main/osh/openstack/06-keystone/README.md).

---

### Deploy Glance
- Follow the detailed installation instructions [here](https://github.com/pratik705/trinity/blob/main/osh/openstack/07-glance/README.md).

---

### Deploy Heat
- Follow the detailed installation instructions [here](https://github.com/pratik705/trinity/blob/main/osh/openstack/08-heat/README.md).

---

### Deploy Cinder
- Follow the detailed installation instructions [here](https://github.com/pratik705/trinity/blob/main/osh/openstack/09-cinder/README.md).

--- 

### Deploy Neutron
- Follow the detailed installation instructions [here](https://github.com/pratik705/trinity/blob/main/osh/openstack/10-neutron/README.md).

---

### Deploy Placement
- Follow the detailed installation instructions [here](https://github.com/pratik705/trinity/blob/main/osh/openstack/11-placement/README.md).

---

### Deploy Libvirt
- Follow the detailed installation instructions [here](https://github.com/pratik705/trinity/blob/main/osh/openstack/12-libvirt/README.md).

---

### Deploy Nova
- Follow the detailed installation instructions [here](https://github.com/pratik705/trinity/blob/main/osh/openstack/13-nova/README.md).

---

### Deploy Octavia
- Follow the detailed installation instructions [here](https://github.com/pratik705/trinity/blob/main/osh/openstack/14-octavia/README.md).

--- 

### Deploy Horizon
- Follow the detailed installation instructions [here](https://github.com/pratik705/trinity/blob/main/osh/openstack/15-horizon/README.md).

---