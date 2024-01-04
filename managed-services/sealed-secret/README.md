# Sealed-secrets

Sealed-secret encrypts plain-text secrets, ensuring secure storage in a Git repository.

Download `kubeseal` binary. You can refer [this](https://github.com/bitnami-labs/sealed-secrets?tab=readme-ov-file#linux) link for the same.

Once sealed-secret is deployed, you can save sealed secret certificates, which will be used to encrypt Kubernetes secret resources when deploying openstack-helm.
```bash
kubectl get secret sealed-secrets-<xxxx>  -o jsonpath="{['data']['tls\.key']}"  -n rackspace-system | base64 -d > ../../tools/sealed-secret-tls.key

kubeseal --controller-namespace rackspace-system  --controller-name sealed-secrets --fetch-cert > ../../tools/sealed-secret-tls.crt
```
**Note:** Make sure to take a backup of sealed-secret-tls.key and sealed-secret-tls.crt.

For any changes or customization, modify the `values.yaml` file or create Kubernetes manifest file.