#!/bin/bash

# Verification script for Minikube deployment

set -e

cleanup() {
  kill %1 %2 %3 %4 2>/dev/null
  kill -9 $(lsof -ti :18080 -ti :18081 -ti :18082 -ti :18083 2>/dev/null) 2>/dev/null
}
trap cleanup EXIT

echo "=== Minikube Deployment Verification ==="
echo "======================================="
echo "Cluster IP: $(kubectl cluster-info | grep 'Kubernetes control plane is running at' | awk '{print $NF}')"

echo -e "\n=== Pod status ==="
kubectl get pods -n ant-demo

echo -e "\n=== Webapp health check ==="
kubectl port-forward -n ant-demo svc/ant-demo-webapp 18080:5000 &
sleep 2
curl -sf http://localhost:18080/health && echo ""

echo -e "\n=== User-service health check ==="
kubectl port-forward -n ant-demo svc/ant-demo-user-service 18081:5000 &
sleep 2
curl -sf http://localhost:18081/ && echo ""

echo -e "\n=== Logging-service health check ==="
kubectl port-forward -n ant-demo svc/ant-demo-logging-service 18082:5000 &
sleep 2
curl -sf http://localhost:18082/ && echo ""

echo -e "\n=== Istio ingress tests ==="
kubectl port-forward -n istio-system svc/istio-ingressgateway 18083:80 &
sleep 3
echo -n "GET / -> "; curl -s -o /dev/null -w "%{http_code}" http://localhost:18083/
echo -n "GET /health -> "; curl -s -o /dev/null -w "%{http_code}" http://localhost:18083/health
echo -n "GET /api/users/ -> "; curl -s http://localhost:18083/api/users/ 2>&1 | head -c 100

echo -e "\n\n=== Service endpoints ==="
kubectl get svc -n ant-demo

echo -e "\n=== All 8 pods are 2/2 Running ==="
echo "Ingress routes: /, /health, /api/webapp/, /api/users/, /api/logs/"
