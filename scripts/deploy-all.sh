#!/bin/bash

# Enable automatic sidecar injection for ant-demo namespace
echo "=== Setting up ant-demo namespace ==="
kubectl apply -f k8s/istio/namespace.yaml

# Deploy Istio addons (Prometheus, Kiali, Jaeger)
echo "=== Deploying Istio addons ==="
kubectl apply -f k8s/istio/observability/prometheus-addon.yaml
kubectl apply -f k8s/istio/observability/kiali-addon.yaml
kubectl apply -f k8s/istio/observability/jaeger-addon.yaml

# Deploy security policies
echo "=== Deploying security policies ==="
kubectl apply -f k8s/istio/security/

# Deploy application services
echo "=== Deploying application services ==="
kubectl apply -f k8s/deployment.yml
kubectl apply -f k8s/service.yml
kubectl apply -f k8s/storage-class.yml

# Deploy PostgreSQL
echo "=== Deploying PostgreSQL ==="
kubectl apply -f k8s/postgres.yml

# Deploy Istio resources
echo "=== Deploying Istio resources ==="
kubectl apply -f k8s/istio/gateway.yaml
kubectl apply -f k8s/istio/virtualservices/
kubectl apply -f k8s/istio/destinationrules/

echo "=== Deployment complete ==="
