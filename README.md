# Ant Demo Application

A comprehensive Kubernetes cluster application showcase demonstrating modern cloud native development and operations practices. This project serves as a learning resource for developers and SREs, covering everything from simple Flask applications to advanced microservices architectures.

## Project Overview

The Ant Demo application has evolved through multiple phases, each demonstrating different architectural patterns and Kubernetes features. What started as a simple "Hello World" Flask app has grown into a full microservices architecture with API gateway, gRPC services, and Kubernetes-native routing.

### Application Phases

This project demonstrates the progression from a simple monolithic application to a sophisticated microservices architecture:

| Phase | Version | Features | Status |
|-------|---------|----------|--------|
| Phase 1 | v1-v3 | Flask app with progressive features | Complete |
| Phase 2.1 | v4 | Kong Gateway + Microservices + gRPC | Complete |
| Phase 2.2 | v5 | Real-time WebSocket metrics + Prometheus | Current |
| Phase 2.3 | v6 | Service mesh (Istio) | Planned |
| Phase 2.4 | v7 | Event-driven architecture | Planned |

---

## Phase 1: Foundation

### Version 1 - Hello World

The simplest version displays "Hello World" - perfect for learning Flask basics.

```bash
docker build -t ant-demo:v1 .
docker run -p 5000:5000 ant-demo:v1
# Access: http://localhost:5000
```

### Version 2 - System Information

Displays OS information (CPU, memory, disk, network) - demonstrates system monitoring.

```bash
docker build -t ant-demo:v2 .
docker run -p 5000:5000 -e APP_VERSION=2 ant-demo:v2
# Access: http://localhost:5000
```

### Version 3 - PostgreSQL Logging

Logs access to PostgreSQL database and displays recent logs - introduces database integration.

```bash
cp .env.example .env
docker build -t ant-demo:v3 .
docker-compose up -d
# Access: http://localhost:5001
```

---

## Phase 2.2: Real-time Metrics (Current)

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     Kong API Gateway                          │
│     Ports: 8000 (HTTP), 8443 (TLS), 9000 (gRPC), 8001 (Admin)  │
└────────────────────────────┬────────────────────────────────────┘
                             │
            ┌─────────────────┼─────────────────┐
            │                 │                 │
            ▼                 ▼                 ▼
    ┌────────────┐    ┌────────────┐    ┌────────────┐
    │   Webapp   │    │    User    │    │  Logging   │
    │    (v5)    │    │  Service  │    │  Service   │
    │ :5000 + WS │    │ :50051 gRPC│    │ :50052 gRPC│
    └─────┬──────┘    └─────┬──────┘    └─────┬──────┘
          │                 │                 │
          └─────────────────┼─────────────────┘
                             │
                             ▼
                    ┌───────────────┐
                    │  PostgreSQL   │
                    │  :5432        │
                    └───────────────┘
```

### New Features

| Feature | Description |
|---------|-------------|
| **WebSocket Metrics** | Real-time system metrics streaming at 2-second intervals |
| **Chart.js Dashboard** | 5 interactive charts showing CPU, memory, disk, network metrics |
| **Prometheus Integration** | Metrics endpoint `/api/webapp/metrics` with custom collectors |
| **Metrics Collection** | Background thread collecting system data via psutil |

### Services

| Service | Port | Protocol | Description |
|---------|------|----------|-------------|
| Webapp (v5) | 5000 | HTTP + WebSocket | Real-time metrics dashboard |
| Kong Gateway | 8000 | HTTP | API routing |
| Kong Admin | 8001 | HTTP | Gateway management |
| Prometheus Scraper | n/a | HTTP | Metrics collection (configurable) |

### Prometheus Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `antdemo_requests_total` | Counter | Total HTTP requests received |
| `antdemo_request_duration_seconds` | Histogram | Request latency |
| `antdemo_active_connections` | Gauge | Active WebSocket connections |
| `antdemo_system_cpu` | Gauge | System CPU usage percentage |
| `antdemo_system_memory` | Gauge | System memory usage percentage |
| `antdemo_system_disk` | Gauge | System disk usage percentage |
| `antdemo_system_net_sent` | Gauge | Network bytes sent |
| `antdemo_system_net_recv` | Gauge | Network bytes received |
| `antdemo_database_queries` | Counter | Database queries executed |
| `antdemo_errors_total` | Counter | Application errors |

### Accessing the Dashboard

```bash
# Run v5 directly
docker run -d --name ant-demo-webapp-1 --network ant-demo_default --env-file .env -e APP_VERSION=5 -p 5001:5000 --hostname webapp ant-demo-webapp

# Access via Kong
curl http://localhost:8000/api/webapp/health  # Check health
curl http://localhost:8000/api/webapp/metrics  # Prometheus endpoint
open http://localhost:8000/api/webapp/  # Open dashboard
```

---

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         Kong API Gateway                          │
│     Ports: 8000 (HTTP), 8443 (TLS), 9000 (gRPC), 8001 (Admin)   │
└────────────────────────────┬────────────────────────────────────┘
                             │
           ┌─────────────────┼─────────────────┐
           │                 │                 │
           ▼                 ▼                 ▼
    ┌────────────┐    ┌────────────┐    ┌────────────┐
    │   Webapp   │    │    User    │    │  Logging   │
    │    (UI)    │    │  Service  │    │  Service   │
    │   :5000    │    │ :50051 gRPC│    │ :50052 gRPC│
    └─────┬──────┘    └─────┬──────┘    └─────┬──────┘
          │                 │                 │
          └─────────────────┼─────────────────┘
                             │
                             ▼
                    ┌───────────────┐
                    │  PostgreSQL   │
                    │  :5432        │
                    └───────────────┘
```

### Services

| Service | Port | Protocol | Description |
|---------|------|----------|-------------|
| Kong Gateway | 8000 | HTTP | Centralized routing |
| Kong Admin | 8001 | HTTP | Gateway management |
| Kong gRPC | 9000 | gRPC | gRPC proxying |
| Webapp | 5000 | HTTP | UI service (v4) |
| User Service | 50051 | gRPC | User management |
| Logging Service | 50052 | gRPC | Access logging |

### Kong Routes

| Path | Service | Upstream | Description |
|------|---------|----------|-------------|
| /api/webapp/* | webapp | webapp:5000 | UI routes |
| /api/users/* | user-service | user-service:5000 | User management |
| /api/logs/* | logging-service | logging-service:5000 | Logging operations |

### gRPC Services

#### User Service (port 50051)

```protobuf
service UserService {
  rpc GetUser(GetUserRequest) returns (UserResponse);
  rpc CreateUser(CreateUserRequest) returns (UserResponse);
  rpc UpdateUser(UpdateUserRequest) returns (UserResponse);
  rpc DeleteUser(DeleteUserRequest) returns (UserResponse);
  rpc ListUsers(ListUsersRequest) returns (ListUsersResponse);
}
```

#### Logging Service (port 50052)

```protobuf
service LoggingService {
  rpc CreateLog(CreateLogRequest) returns (LogResponse);
  rpc GetLogs(GetLogsRequest) returns (GetLogsResponse);
}
```

---

## Getting Started

### Quick Start

```bash
# Clone the repository
git clone https://github.com/moesix/ant-demo.git
cd ant-demo

# Start all services
docker compose up -d

# Wait for services to be ready
sleep 10

# Verify all services are healthy
curl http://localhost:8000/api/webapp/health
curl http://localhost:8000/api/users/health
curl http://localhost:8000/api/logs/health
```

### Local Development

```bash
# Build individual services
docker build -t ant-demo:webapp ./webapp
docker build -t ant-demo:user-service ./user-service
docker build -t ant-demo:logging-service ./logging-service

# Run with Docker Compose
docker compose up -d

# Check service status
docker compose ps

# View logs
docker compose logs webapp
docker compose logs kong
```

### Testing the Application

```bash
# Test UI through Kong
curl http://localhost:8000/api/webapp/
curl http://localhost:8000/api/webapp/health

# Test microservices
curl http://localhost:8000/api/users/health
curl http://localhost:8000/api/logs/health

# Test Kong Admin
curl http://localhost:8001/status
curl http://localhost:8001/services
curl http://localhost:8001/routes
```

---

## Kong Gateway Configuration

### Declarative Configuration

The Kong Gateway uses declarative configuration defined in `kong/kong.yml`:

```yaml
services:
  - name: webapp-service
    url: http://webapp:5000
    
  - name: user-service
    url: http://user-service:5000
    
  - name: logging-service
    url: http://logging-service:5000

routes:
  - name: webapp-route
    paths: ["/api/webapp"]
    service: webapp-service
    
  - name: user-service-route
    paths: ["/api/users"]
    service: user-service
    
  - name: logging-service-route
    paths: ["/api/logs"]
    service: logging-service
```

### Managing Kong

```bash
# Reload configuration
curl -X POST http://localhost:8001/admin-api/reload

# Add a new route
curl -X POST http://localhost:8001/services \
  -d "name=new-service" \
  -d "url=http://new-service:5000"

# Enable/disable plugins
curl -X POST http://localhost:8001/plugins \
  -d "name=rate-limiting" \
  -d "config.minute=100"
```

---

## gRPC API Reference

### User Service

```bash
# Get user by ID
grpcurl -plaintext -d '{"id": 1}' localhost:50051 user.UserService/GetUser

# Create user
grpcurl -plaintext -d '{"name": "John", "email": "john@example.com", "password": "secret"}' \
  localhost:50051 user.UserService/CreateUser

# List all users
grpcurl -plaintext localhost:50051 user.UserService/ListUsers

# Update user
grpcurl -plaintext -d '{"id": 1, "name": "Jane", "email": "jane@example.com", "password": "newsecret"}' \
  localhost:50051 user.UserService/UpdateUser

# Delete user
grpcurl -plaintext -d '{"id": 1}' localhost:50051 user.UserService/DeleteUser
```

### Logging Service

```bash
# Create log entry
grpcurl -plaintext -d '{"message": "User logged in"}' \
  localhost:50052 logging.LoggingService/CreateLog

# Get recent logs
grpcurl -plaintext -d '{"limit": 10}' localhost:50052 logging.LoggingService/GetLogs
```

---

## Kubernetes Deployment

### Prerequisites

- Kubernetes cluster (Minikube, GKE, EKS, AKS)
- kubectl configured
- Helm 3.x (for Helm deployment)
- Kong Gateway CRDs (for Gateway API)

### Deploy with Traditional Manifests

```bash
# Deploy all resources
kubectl apply -f k8s/

# Check deployment status
kubectl get deployments
kubectl get services
kubectl get pods

# View logs
kubectl logs -l app=webapp
```

### Deploy with Kong Gateway API

```bash
# Deploy Kong resources
kubectl apply -f k8s/kong/

# Check Gateway status
kubectl get gatewayclass
kubectl get gateway -n kong
kubectl get httproute

# Access the application
kubectl get gateway -n kong -o jsonpath='{.status.addresses}'
```

### Deploy with Helm

```bash
# Add Traefik repository
helm repo add traefik https://helm.traefik.io/traefik
helm repo update

# Install Traefik ingress controller
helm install traefik traefik/traefik --namespace traefik --create-namespace

# Deploy application
cd charts/ant-demo
helm dependency update
helm install ant-demo . --namespace ant-demo --create-namespace
```

---

## CI/CD Pipeline

The GitHub Actions workflow (`.github/workflows/ci-cd.yml`) automates:

1. **Build**: Docker image construction
2. **Test**: Run pytest and Playwright tests
3. **Security**: Trivy image scanning, SNYK dependency scanning
4. **Push**: Image to GitHub Container Registry
5. **Deploy**: To AWS EKS cluster

### Triggering the Pipeline

```bash
git add .
git commit -m "Your commit message"
git push origin main
```

---

## Testing

### Run Tests Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run unit and integration tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=. --cov-report=html

# Open coverage report
open htmlcov/index.html
```

### Run Tests in Docker

```bash
docker compose exec webapp python -m pytest tests/ -v
```

---

## What's Next

### Phase 2.2: Real-time Metrics (v5)

- WebSocket server for live metrics
- React dashboard with interactive charts
- Prometheus integration with custom collectors

### Phase 2.3: Service Mesh (Istio)

- mTLS between services
- Traffic management
- Distributed tracing with Jaeger

### Phase 2.4: Event-Driven Architecture

- RabbitMQ integration
- Message producer/consumer pattern
- Dead letter queue implementation

### Phase 3: Security Hardening

- Pod Security Standards
- Network Policies
- HashiCorp Vault integration

### Phase 4: Performance Optimization

- Redis caching
- Database query optimization
- CDN integration

---

## Project Structure

```
ant-demo/
├── app.py                      # Webapp UI service (Flask)
├── requirements.txt            # Python dependencies
├── Dockerfile              # Multi-stage Docker build
├── docker-compose.yml        # Docker Compose orchestration
├── kong/
���   └── kong.yml           # Kong declarative configuration
├── k8s/
│   ├── deployment.yml     # Kubernetes deployment
│   ├── service.yml      # Kubernetes services
│   └── kong/           # Kong Gateway API resources
│       ├── gatewayclass.yaml
│       ├── gateway.yaml
│       ├── credentials.yaml
│       └── kong-routes.yaml
├── user-service/
│   ├── app.py           # User service (Flask + gRPC)
│   ├── Dockerfile
│   └── protobuf/        # gRPC definitions
├── logging-service/
│   ├── app.py         # Logging service (Flask + gRPC)
│   ├── Dockerfile
│   └── protobuf/       # gRPC definitions
├── scripts/
│   └── init-db.sh      # Database initialization
├── static/
│   └── style.css
└── templates/
    └── index.html
```

---

## Documentation

| Document | Description |
|----------|-------------|
| [CHANGELOG.md](CHANGELOG.md) | Release history and changes |
| [k8s-plan.md](k8s-plan.md) | Enhancement roadmap |
| [documentation/walkthrough.md](documentation/walkthrough.md) | Step-by-step guide for Phase 1 |