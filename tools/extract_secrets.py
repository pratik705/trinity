import os
import yaml
import argparse

def has_secrets(file_path):
    with open(file_path, 'r') as file:
        manifest = yaml.safe_load_all(file)
        for resource in manifest:
            if resource is not None and resource.get('kind') == 'Secret':
                return True
    return False

def has_only_secrets(file_path):
    resource_type = {}
    with open(file_path, 'r') as file:
        manifest = yaml.safe_load_all(file)
        for resource in manifest:
            if resource is not None:
                resource_type['type']= resource.get('kind')
    if resource_type['type'] == 'Secret':
        return True 
    return False

def extract_secrets(manifest_dir):
    for root, dirs, files in os.walk(manifest_dir):
        for filename in files:
            file_path = os.path.join(root, filename)

            if filename.endswith(".yaml") or filename.endswith(".yml"):
                print(f"Processing file: {file_path}")                
                if not has_secrets(file_path):
                    print(f"Ignoring file: {file_path} as it doesn't contain any Kubernetes Secret resources")
                    continue
                if  has_only_secrets(file_path):
                    print(f"Ignoring file: {file_path} as it contains only Kubernetes Secret resources")
                    continue 
                with open(file_path, 'r') as file:
                    manifest = yaml.safe_load_all(file)

                    new_manifest = []
                    secrets = []

                    for resource in manifest:
                        if resource is not None:
                            if resource.get('kind') == 'Secret':
                                secrets.append(resource)
                            else:
                                new_manifest.append(resource)

                    secrets_file_path = os.path.join(root, f'secrets_{filename}')

                    with open(secrets_file_path, 'w') as secrets_file:
                        yaml.dump_all(secrets, secrets_file, default_flow_style=False)
                        print(f"Extracted secret resource from {filename} to {secrets_file_path}")

                    with open(os.path.join(root, f'new_manifest_{filename}'), 'w') as new_manifest_file:
                        yaml.dump_all(new_manifest, new_manifest_file, default_flow_style=False)

                    os.rename(os.path.join(root, f'new_manifest_{filename}'), file_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Extract secrets from Kubernetes manifest files')
    parser.add_argument('directory', metavar='directory', type=str, help='Path to the directory containing Kubernetes manifest files')

    args = parser.parse_args()
    extract_secrets(args.directory)
