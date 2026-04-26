#!/bin/bash

# Deployment script for Minikube with GHCR integration

set -e

# Check if GHCR_TOKEN_RW is set
if [ -z "$GHCR_TOKEN_RW" ]; then
  echo "Error: GHCR_TOKEN_RW environment variable not set"
  echo "Please run: export GHCR_TOKEN_RW=<your-token>"
  exit 1
fi

echo "=== Minikube Deployment Script ==="
echo "=================================="
echo "Using GHCR token: ${GHCR_TOKEN_RW:0:5}..."

# Step 1: Validate cluster connection
echo -e "\n=== Step 1: Validating cluster connection ==="
if ! kubectl cluster-info &>/dev/null; then
  echo "Error: Cannot connect to Kubernetes cluster"
  exit 1
fi

CLUSTER_IP=$(kubectl cluster-info | grep 'Kubernetes control plane is running at' | awk '{print $NF}')
echo "Cluster found at: $CLUSTER_IP"

# Step 2: Create ant-demo namespace with istio-injection
echo -e "\n=== Step 2: Creating ant-demo namespace ==="
kubectl apply -f k8s/istio/namespace.yaml
kubectl label namespace ant-demo istio-injection=enabled --overwrite

# Step 3: Create ghcr-creds secret for image pull
echo -e "\n=== Step 3: Creating ghcr-creds secret ==="
kubectl create secret docker-registry ghcr-creds \
  --docker-server=ghcr.io \
  --docker-username=moe6 \
  --docker-password="$GHCR_TOKEN_RW" \
  --namespace=ant-demo \
  --dry-run=client -o yaml | kubectl apply -f -

# Step 4: Create postgres-credentials secret
echo -e "\n=== Step 4: Creating postgres-credentials secret ==="
kubectl create secret generic postgres-credentials \
  --from-literal=user=antdemo \
  --from-literal=password=strongpassword \
  --namespace=ant-demo \
  --dry-run=client -o yaml | kubectl apply -f -

# Step 5: Deploy PostgreSQL
echo -e "\n=== Step 5: Deploying PostgreSQL ==="
kubectl apply -f k8s/postgres.yml

# Step 6: Wait for PostgreSQL to be ready
echo -e "\n=== Step 6: Waiting for PostgreSQL to be ready ==="
for i in {1..30}; do
  if kubectl get pods -n ant-demo -l app=postgres-db 2>/dev/null | grep -E '2/2.*Running' >/dev/null; then
    echo "✓ PostgreSQL is ready"
    break
  fi
  echo "Waiting for PostgreSQL... ($i/30)"
  sleep 2
done

# Check if PostgreSQL is actually ready
if ! kubectl get pods -n ant-demo -l app=postgres-db 2>/dev/null | grep -E '2/2.*Running' >/dev/null; then
  echo "Error: PostgreSQL not ready after 60 seconds"
  kubectl get pods -n ant-demo -l app=postgres-db
  exit 1
fi

# Step 7: Deploy app services
echo -e "\n=== Step 7: Deploying application services ==="
kubectl apply -f k8s/deployment.yml
kubectl apply -f k8s/service.yml

# Step 8: Deploy Istio resources
echo -e "\n=== Step 8: Deploying Istio resources ==="
# Skip prometheus and kiali addons - they're already installed via Istio demo profile
kubectl apply -f k8s/istio/observability/jaeger-addon.yaml
kubectl apply -f k8s/istio/security/
kubectl apply -f k8s/istio/destinationrules/
kubectl apply -f k8s/istio/virtualservices/
kubectl apply -f k8s/istio/gateway.yaml

# Step 9: Wait for all app services to be ready
echo -e "\n=== Step 9: Waiting for all services to be ready ==="
echo "Checking webapp..."
for i in {1..60}; do
  if kubectl get pods -n ant-demo -l app=ant-demo-webapp 2>/dev/null | grep -E '1/1.*Running' >/dev/null; then
    echo "✓ Webapp is ready"
    break
  fi
  echo "Waiting for webapp... ($i/60)"
  sleep 2
done

echo "Checking user-service..."
for i in {1..60}; do
  if kubectl get pods -n ant-demo -l app=ant-demo-user-service 2>/dev/null | grep -E '1/1.*Running' >/dev/null; then
    echo "✓ User-service is ready"
    break
  fi
  echo "Waiting for user-service... ($i/60)"
  sleep 2
done

echo "Checking logging-service..."
for i in {1..60}; do
  if kubectl get pods -n ant-demo -l app=ant-demo-logging-service 2>/dev/null | grep -E '1/1.*Running' >/dev/null; then
    echo "✓ Logging-service is ready"
    break
  fi
  echo "Waiting for logging-service... ($i/60)"
  sleep 2
done

# Verify all pods are running
echo -e "\n=== Final pod status ==="
kubectl get pods -n ant-demo

echo -e "\n=== Deployment complete! ==="
echo -e "\nNext steps:"
echo "1. Run 'scripts/verify-minikube.sh' to verify all endpoints"
echo "2. Access Jaeger: kubectl port-forward -n istio-system svc/jaeger 16686:16686"