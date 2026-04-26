# Istio Service Mesh Setup

## Overview
This document provides detailed instructions for deploying and managing the Istio service mesh for the Ant Demo application.

## Prerequisites
- Kubernetes cluster running Kubernetes 1.19+
- istioctl CLI tool
- kubectl CLI tool configured with cluster access

## Installation

### Step 1: Download and Install Istioctl
```bash
curl -L https://istio.io/downloadIstio.sh | sh -
export PATH=$PATH:$HOME/istio-*/bin
```

### Step 2: Install Istio Control Plane
```bash
istioctl install --set profile=demo --skip-confirmation
```

### Step 3: Verify Installation
```bash
kubectl get pods -n istio-system
kubectl get svc -n istio-system
```

## Application Deployment

### Step 1: Configure Namespace
```bash
kubectl apply -f k8s/istio/namespace.yaml
```

### Step 2: Deploy Application Resources
```bash
kubectl apply -f k8s/deployment.yml
kubectl apply -f k8s/service.yml
kubectl apply -f k8s/storage-class.yml
```

### Step 3: Deploy Istio Resources
```bash
kubectl apply -f k8s/istio/gateway.yaml
kubectl apply -f k8s/istio/virtualservices/
kubectl apply -f k8s/istio/destinationrules/
kubectl apply -f k8s/istio/security/
```

## One-Command Deployment
```bash
./scripts/deploy-all.sh
```

## Verification

### Check Service Status
```bash
kubectl get pods -n ant-demo
kubectl get svc -n ant-demo
```

### Verify Sidecar Injection
```bash
kubectl get pods -n ant-demo -o jsonpath='{.items[*].spec.containers[*].name}' | grep istio-proxy
```

### Verify Istio Resources
```bash
kubectl get virtualservices -n ant-demo
kubectl get destinationrules -n ant-demo
kubectl get peerauthentication -A
kubectl get authorizationpolicy -n ant-demo
```

### Run Full Verification
```bash
./scripts/verify-deployment.sh
```

## Observability

### Kiali Dashboard
```bash
istioctl dashboard kiali
```

### Prometheus Dashboard
```bash
istioctl dashboard prometheus
```

### Jaeger Dashboard
```bash
istioctl dashboard jaeger
```

### Grafana Dashboard
```bash
istioctl dashboard grafana
```

## Traffic Management

### Canary Deployment Example
```bash
# Deploy v5 and v6 versions
kubectl apply -f k8s/deployments/webapp-v5.yaml
kubectl apply -f k8s/deployments/webapp-v6.yaml

# Create destination rule with subsets
kubectl apply -f k8s/istio/destinationrules/webapp-destinationrule.yaml

# Configure virtual service with 90% traffic to v5, 10% to v6
kubectl apply -f k8s/istio/virtualservices/webapp-canary.yaml
```

## Security

### mTLS Verification
```bash
kubectl exec -it $(kubectl get pod -l app=ant-demo-webapp -o jsonpath='{.items[0].metadata.name}') -c istio-proxy -- curl -v http://ant-demo-user-service:5000
```

### Check Authorization Policies
```bash
kubectl describe authorizationpolicy -n ant-demo
```

## Fault Injection Testing

### Test Delays
```bash
kubectl apply -f k8s/istio/virtualservices/webapp-virtualservice.yaml
kubectl exec -it $(kubectl get pod -l app=ant-demo-webapp -o jsonpath='{.items[0].metadata.name}') -c webapp -- curl -w "@curl-format.txt" http://ant-demo-user-service:5000
```

### Test Circuit Breakers
```bash
# Override destination rule with circuit breaker settings
kubectl apply -f k8s/istio/destinationrules/webapp-circuit-breaker.yaml

# Send high traffic to trigger circuit breaker
ab -n 1000 -c 100 http://ant-demo-webapp:5000/api/webapp/
```

## Cleanup

### Full Cleanup
```bash
./scripts/cleanup.sh
```

### Uninstall Istio Only
```bash
istioctl x uninstall --purge -y
```

## Troubleshooting

### Common Issues

#### 1. Sidecar Injection Not Happening
```bash
kubectl get namespace ant-demo -o jsonpath='{.metadata.labels}'
kubectl label namespace ant-demo istio-injection=enabled --overwrite
```

#### 2. Services Not Reachable
```bash
istioctl analyze
kubectl describe virtualservice -n ant-demo
kubectl describe destinationrule -n ant-demo
```

#### 3. mTLS Handshake Failures
```bash
istioctl pc secret $(kubectl get pod -l app=ant-demo-webapp -o jsonpath='{.items[0].metadata.name}') -c istio-proxy
```

#### 4. Metrics Not Scraping
```bash
kubectl get pod -l app=ant-demo-webapp -o jsonpath='{.items[0].metadata.annotations}'
kubectl logs $(kubectl get pod -l app=ant-demo-webapp -o jsonpath='{.items[0].metadata.name}') -c istio-proxy
```

## Architecture

### Traffic Flow
```
External → Kong Gateway → Istio Ingress → Service Mesh → Services
```

### Components
- **Kong Gateway**: External API management with rate limiting, auth
- **Istio Ingress Gateway**: TLS termination, mTLS to internal services
- **Istiod**: Istio control plane
- **Envoy Sidecars**: Traffic management, security, observability
- **Prometheus**: Metrics collection
- **Kiali**: Service mesh visualization
- **Jaeger**: Distributed tracing

## References
- [Istio Documentation](https://istio.io/docs/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Istio Best Practices](https://istio.io/latest/docs/ops/best-practices/)
