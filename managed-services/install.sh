#!/bin/bash

while true; do
    kubectl kustomize --enable-helm=true . | kubectl apply -f -
    if [ $? -eq 0 ]; then
        echo "All resources installed successfully."
        break
    else
        echo "Retrying in 5 seconds..."
        sleep 5
    fi
done
