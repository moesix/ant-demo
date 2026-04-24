# Kubernetes Demo Application Walkthrough

## Introduction

Welcome to the Kubernetes Demo Application walkthrough! This guide is designed for DevOps learners who want to understand how to build, containerize, test, and deploy a modern web application using Kubernetes. We'll cover everything from local development with Docker to production deployment on Kubernetes, with CI/CD pipelines and comprehensive testing.

## Prerequisites

Before you begin, make sure you have the following tools installed:

1. Docker
2. Docker Compose
3. Kubernetes CLI (kubectl)
4. Helm (for chart deployment)
5. Python 3.11+
6. Git

## Phase 1: Project Setup

### 1.1 Clone the Repository

First, clone the repository to your local machine:

```bash
git clone https://github.com/moesix/ant-demo.git
cd ant-demo
```

### 1.2 Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
# or
.\venv\Scripts\activate  # On Windows
```

### 1.3 Install Dependencies

```bash
pip install -r requirements.txt
```

## Phase 2: Application Overview

### 2.1 Application Architecture

The application is a Python Flask web app with three versions:

- **v1**: Displays "Hello World"
- **v2**: Shows system information (CPU, memory, disk, network)
- **v3**: Logs access to PostgreSQL and displays recent logs

### 2.2 Database Setup

For v3, we use PostgreSQL. The application uses Flask-SQLAlchemy for ORM and Flask-Migrate for database migrations.

## Phase 3: Local Development with Docker

### 3.1 Build the Docker Image

```bash
docker build -t ant-demo:v3 .
```

### 3.2 Run with Docker Compose

```bash
cp .env.example .env
docker-compose up -d
```

This will start:
- A Flask web app container (v3)
- A PostgreSQL container
- A pgAdmin container (for database management)

### 3.3 Verify the Application

Access the application at http://localhost:5001

Check the containers:
```bash
docker-compose ps
```

### 3.4 Database Management

Check if the access_logs table exists:
```bash
docker-compose exec postgres_db psql -U antuser -d antdemo -c "SELECT * FROM access_logs;"
```

## Phase 4: Testing

### 4.1 Run Tests Locally

```bash
python -m pytest tests/ -v
```

This will run:
- Unit tests (tests/test_app.py, tests/test_database.py)
- Integration tests (tests/test_database_integration.py)
- End-to-end tests (tests/test_e2e.py)

### 4.2 Test Coverage

Generate a coverage report:
```bash
python -m pytest tests/ --cov=. --cov-report=html
```

Open htmlcov/index.html in your browser to view the coverage report.

### 4.3 Run Tests Inside Docker

```bash
docker-compose exec webapp python -m pytest tests/ -v
```

## Phase 5: Kubernetes Deployment

### 5.1 Minikube Setup

Start a local Kubernetes cluster with Minikube:
```bash
minikube start
```

### 5.2 Deploy with Helm

First, install Traefik ingress controller:
```bash
helm repo add traefik https://helm.traefik.io/traefik
helm repo update
helm install traefik traefik/traefik --namespace traefik --create-namespace
```

Then deploy the application:
```bash
cd charts/ant-demo
helm dependency update
helm install ant-demo . --namespace ant-demo --create-namespace
```

### 5.3 Monitor Deployment

```bash
kubectl get pods -n ant-demo
kubectl get services -n ant-demo
kubectl get ingressroutes -n ant-demo
```

### 5.4 Access the Application

Get the Traefik LoadBalancer IP:
```bash
kubectl get services -n traefik
```

Add an entry to your /etc/hosts file:
```
<TRAEFIK_EXTERNAL_IP> ant-demo.local
```

Access the application at https://ant-demo.local

## Phase 6: CI/CD Pipeline

### 6.1 GitHub Actions Workflow

The .github/workflows/ci-cd.yml file defines the CI/CD pipeline:
- Builds Docker image on code changes
- Runs all tests
- Pushes image to container registry
- Deploys to Kubernetes cluster

### 6.2 Triggering the Pipeline

Push your changes to GitHub:
```bash
git add .
git commit -m "Your commit message"
git push origin main
```

## Phase 7: Monitoring and Debugging

### 7.1 Check Logs

```bash
kubectl logs -n ant-demo deployment/ant-demo-webapp
```

### 7.2 Check Metrics

If you have Prometheus and Grafana installed:
```bash
kubectl port-forward -n monitoring service/grafana 3000:80
```

Access Grafana at http://localhost:3000

### 7.3 Debugging Containers

```bash
kubectl exec -n ant-demo -it <pod-name> /bin/bash
```

## Phase 8: Cleanup

### 8.1 Stop Local Services

```bash
docker-compose down
minikube stop
```

### 8.2 Uninstall Kubernetes Resources

```bash
helm uninstall ant-demo --namespace ant-demo
kubectl delete namespace ant-demo
helm uninstall traefik --namespace traefik
kubectl delete namespace traefik
```

## Conclusion

Congratulations! You've successfully completed the Kubernetes Demo Application walkthrough. You've learned how to:
- Build and containerize a Python Flask application
- Run and test the application locally with Docker
- Deploy the application to a Kubernetes cluster using Helm
- Set up CI/CD pipelines with GitHub Actions
- Monitor and debug Kubernetes resources

This project is a great foundation for learning more about Kubernetes and DevOps practices. Feel free to experiment with different configurations and features!