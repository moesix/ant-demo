#!/bin/bash
set -e

# Create GHCR pull secret for Kubernetes
# This secret allows Kubernetes to pull images from GHCR

# Check if secret already exists
if kubectl get secret ghcr-creds -n ant-demo &>/dev/null; then
    echo "ghcr-creds secret already exists"
else
    echo "Creating ghcr-creds secret..."
    kubectl create secret docker-registry ghcr-creds \
      --docker-server=ghcr.io \
      --docker-username=moe6 \
      --docker-password=${GHCR_TOKEN:-placeholder} \
      --namespace=ant-demo
    echo "ghcr-creds secret created"
fi