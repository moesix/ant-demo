#!/bin/bash

# Cleanup Istio resources
echo "=== Cleaning up Istio resources ==="
kubectl delete -f k8s/istio/destinationrules/ 2>/dev/null || true
kubectl delete -f k8s/istio/virtualservices/ 2>/dev/null || true
kubectl delete -f k8s/istio/gateway.yaml 2>/dev/null || true
kubectl delete -f k8s/istio/security/ 2>/dev/null || true
kubectl delete -f k8s/istio/observability/ 2>/dev/null || true
kubectl delete -f k8s/istio/namespace.yaml 2>/dev/null || true

# Cleanup application resources
echo "=== Cleaning up application resources ==="
kubectl delete -f k8s/deployment.yml 2>/dev/null || true
kubectl delete -f k8s/service.yml 2>/dev/null || true
kubectl delete -f k8s/storage-class.yml 2>/dev/null || true

# Uninstall Istio
echo "=== Uninstalling Istio ==="
istioctl x uninstall --purge -y

echo "=== Cleanup complete ==="
