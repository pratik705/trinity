# Cert-Manager

Cert-Manager automates the management and renewal of TLS certificates. You can request certificates for your applications by defining Certificate resources. Refer to the [Cert-Manager documentation](https://cert-manager.io/docs/) for more information.

It will be deployed in the `rackspace-system` namespace, providing certificate management functionality. Additionally, it configures a CA issuer that applications running in the same namespace can leverage.

For any changes or customization, modify the `values.yaml` file or create Kubernetes manifest file.