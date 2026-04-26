#!/bin/bash

# Verify Istio installation
echo "=== Verifying Istio control plane ==="
kubectl get pods -n istio-system
echo

# Verify application namespace
echo "=== Verifying application namespace ==="
kubectl get namespace ant-demo
echo

# Verify services are running
echo "=== Verifying services ==="
kubectl get svc -n ant-demo
echo

# Verify pods are running with sidecars
echo "=== Verifying pods with sidecars ==="
kubectl get pods -n ant-demo -o jsonpath='{.items[*].spec.containers[*].name}' | grep -E "(istio-proxy|webapp|user-service|logging-service|postgres-db)"
echo

# Verify virtual services and destination rules
echo "=== Verifying Istio resources ==="
kubectl get virtualservices -n ant-demo
kubectl get destinationrules -n ant-demo
echo

# Verify mTLS policy
echo "=== Verifying mTLS policy ==="
kubectl get peerauthentication -A
echo

# Verify authorization policies
echo "=== Verifying authorization policies ==="
kubectl get authorizationpolicy -n ant-demo

echo "=== Verification complete ==="
