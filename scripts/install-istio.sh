#!/bin/bash

# Install Istio control plane with demo profile
echo "=== Installing Istio ==="
istioctl install --set profile=demo --skip-confirmation
if [ $? -ne 0 ]; then
  echo "Error: Failed to install Istio"
  exit 1
fi

# Verify Istio installation
echo "=== Verifying Istio installation ==="
kubectl get pods -n istio-system
echo
kubectl get svc -n istio-system

echo "=== Istio installation complete ==="
