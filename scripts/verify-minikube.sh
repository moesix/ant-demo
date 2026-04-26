#!/bin/bash

# Verification script for Minikube deployment

set -e

echo "=== Minikube Deployment Verification ==="
echo "======================================="
echo "Cluster IP: $(kubectl cluster-info | grep 'Kubernetes control plane is running at' | awk '{print $NF}')"

# Function to run a kubectl exec with curl from the first available pod
run_curl_from_pod() {
  POD=$1
  URL=$2
  
  for i in {1..10}; do
    if kubectl exec -n ant-demo "$POD" -- curl -s -o /dev/null -w "%{http_code}" "$URL" 2>/dev/null; then
      return 0
    fi
    echo "Waiting for pod $POD to be ready..."
    sleep 2
  done
  return 1
}

# Step 1: Check if all pods are running
echo -e "\n=== Step 1: Pod status ==="
kubectl get pods -n ant-demo

# Step 2: Test webapp health from within cluster
echo -e "\n=== Step 2: Webapp health check (from within cluster) ==="
WEBAPP_POD=$(kubectl get pods -n ant-demo -l app=ant-demo-webapp -o name | head -1 | cut -d '/' -f 2)
if run_curl_from_pod "$WEBAPP_POD" "http://ant-demo-webapp:5000/health"; then
  kubectl exec -n ant-demo "$WEBAPP_POD" -- curl -s "http://ant-demo-webapp:5000/health"
else
  echo "❌ Failed to curl webapp"
  exit 1
fi

# Step 3: Test user-service health from within cluster
echo -e "\n=== Step 3: User-service health check (from within cluster) ==="
USER_SERVICE_POD=$(kubectl get pods -n ant-demo -l app=ant-demo-user-service -o name | head -1 | cut -d '/' -f 2)
if run_curl_from_pod "$USER_SERVICE_POD" "http://ant-demo-user-service:5000/"; then
  kubectl exec -n ant-demo "$USER_SERVICE_POD" -- curl -s "http://ant-demo-user-service:5000/"
else
  echo "❌ Failed to curl user-service"
fi

# Step 4: Test logging-service health from within cluster
echo -e "\n=== Step 4: Logging-service health check (from within cluster) ==="
LOGGING_SERVICE_POD=$(kubectl get pods -n ant-demo -l app=ant-demo-logging-service -o name | head -1 | cut -d '/' -f 2)
if run_curl_from_pod "$LOGGING_SERVICE_POD" "http://ant-demo-logging-service:5000/"; then
  kubectl exec -n ant-demo "$LOGGING_SERVICE_POD" -- curl -s "http://ant-demo-logging-service:5000/"
else
  echo "❌ Failed to curl logging-service"
fi

# Step 5: Test webapp via Istio ingress gateway
echo -e "\n=== Step 5: Webapp via Istio ingress ==="
INGRESS_PORT=$(kubectl get svc -n istio-system istio-ingressgateway -o jsonpath='{.spec.ports[?(@.name=="http")].nodePort}')
MINIKUBE_IP=$(minikube ip 2>/dev/null || echo "10.11.11.30")

if curl -s -o /dev/null -w "%{http_code}" "http://$MINIKUBE_IP:$INGRESS_PORT/api/webapp/health" 2>&1; then
  echo -n "Response from /api/webapp/health: "
  curl -s "http://$MINIKUBE_IP:$INGRESS_PORT/api/webapp/health"
else
  echo "❌ Failed to connect to ingress gateway"
  kubectl get svc -n istio-system
fi

# Step 6: Show istioctl authn tls-check
echo -e "\n=== Step 6: Istio authentication status ==="
if command -v istioctl &>/dev/null; then
  istioctl authn tls-check -n ant-demo ant-demo-webapp ant-demo-webapp.ant-demo.svc.cluster.local 5000
else
  echo "istioctl not available"
fi

echo -e "\n=== Verification complete! ==="
echo -e "\nKey information:"
echo "- Istio ingress port: $INGRESS_PORT"
echo "- Minikube IP: $MINIKUBE_IP"
echo "- Webapp endpoint: http://$MINIKUBE_IP:$INGRESS_PORT/api/webapp"
echo "- User-service endpoint: http://$MINIKUBE_IP:$INGRESS_PORT/api/users"
echo "- Logging-service endpoint: http://$MINIKUBE_IP:$INGRESS_PORT/api/logs"
echo -e "\nTo forward Jaeger dashboard to localhost:16686:"
echo "kubectl port-forward -n istio-system svc/jaeger 16686:16686"