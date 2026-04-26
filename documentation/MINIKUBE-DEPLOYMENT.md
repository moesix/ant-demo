# Minikube Deployment Guide

## Prerequisites
- Minikube running with kubectl configured
- GHCR_TOKEN secret in GitHub repository

## Quick Start

### 1. Build and Push Images
```bash
# Go to GitHub Actions tab
# Select "Build, Test, and Deploy to GHCR & EKS" workflow
# Click "Run workflow"
# Select "latest" build type
# Wait for build to complete
```

### 2. Deploy to Minikube
```bash
./scripts/deploy-all.sh
```

### 3. Verify Deployment
```bash
kubectl get pods -n ant-demo
./scripts/verify-deployment.sh
```

## Troubleshooting

### ImagePullBackOff Errors
**Cause:** GHCR credentials not configured

**Solution:**
```bash
kubectl create secret docker-registry ghcr-creds \
  --docker-server=ghcr.io \
  --docker-username=moe6 \
  --docker-password=YOUR_GHCR_TOKEN \
  --namespace=ant-demo
```

### Creating a Personal Access Token (PAT)
1. Go to GitHub > Settings > Developer settings > Personal access tokens (classic)
2. Generate new token
3. Select scopes: `read:packages` (for pulling images)
4. Copy the token and store it somewhere safe
5. Never commit this token to your repository!

### Image Not Found Errors
**Cause:** Images not built or pushed to GHCR

**Solution:**
1. Check the GitHub Actions workflow status
2. Verify that the images exist in the package repository:
   https://github.com/moe6/ant-demo/pkgs/container/ant-demo/
3. If not, trigger the workflow manually from GitHub

## Advanced: Manual Image Loading

If you prefer to build and load images locally instead of pulling from GHCR:

```bash
# Build images directly in Minikube's Docker daemon
eval $(minikube docker-env)
docker build -t ghcr.io/moe6/ant-demo/ant-demo:latest .
docker build -t ghcr.io/moe6/ant-demo/ant-demo-user-service:latest -f user-service/Dockerfile ./user-service/
docker build -t ghcr.io/moe6/ant-demo/ant-demo-logging-service:latest -f logging-service/Dockerfile ./logging-service/

# Or build locally and load into Minikube
docker save ghcr.io/moe6/ant-demo/ant-demo:latest ghcr.io/moe6/ant-demo/ant-demo-user-service:latest ghcr.io/moe6/ant-demo/ant-demo-logging-service:latest > images.tar
kubectl run -n ant-demo temp-pod --image=busybox --rm -i --tty --overrides='{"apiVersion":"v1","spec":{"volumes":[{"name":"docker-sock","hostPath":{"path":"/var/run/docker.sock","type":"Socket"}}],"containers":[{"name":"temp","image":"busybox","volumeMounts":[{"name":"docker-sock","mountPath":"/var/run/docker.sock"}],"command":["sh","-c","wget -qO- https://github.com/moby/moby/releases/download/v24.0.0/docker.tgz | tar -xzO docker > /usr/bin/docker; chmod +x /usr/bin/docker; cat /tmp/images.tar | docker load"],"volumeMounts":[{"name":"docker-sock","mountPath":"/var/run/docker.sock"},{"name":"images","mountPath":"/tmp"}]}],"volumes":[{"name":"docker-sock","hostPath":{"path":"/var/run/docker.sock","type":"Socket"}},{"name":"images","emptyDir":{}}]}}' --attach --image-pull-policy=IfNotPresent
```

## Common Issues and Fixes

### Istio Sidecar Injection Failing
```bash
# Verify injection is enabled
kubectl get namespace ant-demo -o jsonpath='{.metadata.annotations.sidecar\.istio\.io/inject}'

# If not, enable it
kubectl label namespace ant-demo istio-injection=enabled --overwrite
```

### PostgreSQL Connection Issues
```bash
# Check if PostgreSQL pod is running
kubectl get pods -n ant-demo | grep postgres

# Check logs
kubectl logs -n ant-demo $(kubectl get pods -n ant-demo -l app=postgres-db -o jsonpath='{.items[0].metadata.name}')

# Check service is reachable from webapp
kubectl exec -n ant-demo $(kubectl get pods -n ant-demo -l app=ant-demo-webapp -o jsonpath='{.items[0].metadata.name}') -- sh -c 'nc -zv postgres-db 5432'
```