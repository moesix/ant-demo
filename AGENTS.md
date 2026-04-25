# AGENTS.md - OpenCode Instructions for Ant Demo

## Key Changes for Phase 2.3 Development

### Istio Service Mesh Implementation

**New Process Note (2026-04-25):** 
We are implementing ALL Phase 2.3 infrastructure preparation without Minikube first. This includes:
- Kubernetes manifests
- Istio configurations
- Helm charts/templates
- Deployment scripts
- Documentation
- Testing scripts

**Testing & Validation Strategy:**
Once ALL Phase 2.3 preparation is complete, we will deploy to a Minikube cluster for testing and debugging. This approach allows us to:
1. Focus on infrastructure design first
2. Create complete, cohesive configurations
3. Avoid "debugging during deployment" issues
4. Ensure all components work together as designed

**Minikube Deployment Experience:**
- Successfully installed Istio control plane and addons (Jaeger)
- Deployed all three services (webapp, user-service, logging-service) with sidecars
- Added PostgreSQL service and initialized database
- Verified all endpoints respond from within the cluster
- ImagePullBackOff errors resolved by building and loading images locally
- Secrets management implemented for PostgreSQL credentials
- Ingress gateway configuration verified (port 80 ready for traffic)

**Current Minikube Cluster Status:**
- **API Server:** https://10.11.11.30:32771
- **Node Count:** 1 (control-plane)
- **Version:** v1.35.1 (minikube v1.38.1)
- **Resources:** 2 vCPUs, ~4GB RAM, 30GB disk
- **System Pods:** All healthy (coredns, etcd, kube-apiserver, controller-manager, scheduler, proxy, storage-provisioner)

---

## Project Overview
This is a **Python Flask web application project** demonstrating Docker containerization, Kubernetes deployment, and CI/CD pipelines. It supports three application versions (v1, v2, v3) with different features.

## Key Technologies
- **Language:** Python 3.11
- **Framework:** Flask 3.0.0
- **Database:** PostgreSQL 16
- **Containerization:** Docker (multi-stage builds)
- **Orchestration:** Kubernetes
- **CI/CD:** GitHub Actions

## Critical Files and Directories
- `app.py`: Main Flask application (entrypoint)
- `requirements.txt`: Python dependencies
- `Dockerfile`: Multi-stage Docker image definition
- `docker-compose.yml`: Local development with PostgreSQL
- `k8s/`: Kubernetes manifests (deployment, service, storage)
- `.github/workflows/ci-cd.yml`: GitHub Actions pipeline

## Development Commands

### Local Docker
```bash
# Build specific version (v1, v2, or v3)
docker build -t ant-demo:v1 .
docker run -p 5000:5000 ant-demo:v1

# Run with Docker Compose (v3 with PostgreSQL)
docker-compose up
```

### Kubernetes Deployment
```bash
# Apply all manifests
kubectl apply -f k8s/

# Check deployments
kubectl get deployments
kubectl get services
kubectl get pods
```

## Application Versions
- **v1:** Displays "Hello World"
- **v2:** Shows OS information (CPU, memory, disk, network)
- **v3:** Logs access to PostgreSQL database and displays recent logs

## CI/CD Pipeline
- Trigger: Tag pushes matching 'v*' pattern
- Builds and pushes Docker image to GHCR (GitHub Container Registry)
- Deploys to AWS EKS cluster (ap-southeast-1 region)
- Uses rolling updates for zero downtime

## Security Notes
- Docker containers run as non-root user (appuser)
- Kubernetes secrets store sensitive data (e.g., 'postgres-app-creds')
- Image pull secrets ('ghcr-creds') for accessing GitHub Container Registry

## Environment Variables
- See `.env.example` for required variables
- PostgreSQL connection: DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

## Testing
- No explicit test files in repository
- Manual testing via browser or curl
- Health check available at `/health` endpoint

## Changelog Management
- All significant changes must be documented in `CHANGELOG.md`
- Follow the [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format
- Include at least Added, Changed, Removed, and Fixed sections
- Update the changelog before each implementation run