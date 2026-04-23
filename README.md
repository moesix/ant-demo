# Ant Demo Application

This project demonstrates a simple web application designed for Ant, showcasing Docker containerization, Kubernetes deployment, rolling updates, and CI/CD pipelines.

## Project Overview

The application is a Python Flask web application with three distinct versions, each demonstrating different functionalities. It's packaged using Docker and deployed to a Kubernetes cluster, illustrating modern application deployment and management practices.

## Features

### Health Check Endpoint
The application now includes a `/health` endpoint that provides:
- Application health status (healthy/unhealthy)
- Current version information
- Database connection status (for v3)
- System boot time

This endpoint is used by Kubernetes liveness, readiness, and startup probes.

### Programming & Docker

1.  **Simple Web Application (Python Flask):**
    *   **Version 1:** Displays "Hello World".
    *   **Version 2:** Displays OS information (e.g., CPU usage).
    *   **Version 3:** Logs access to the site to a data storage (e.g., PostgreSQL).
2.  **Docker Packaging:** The web application is containerized using Docker. While a data storage solution is mentioned in the requirements, the current project structure primarily focuses on the web application's containerization.
3.  **Version Tagging:** Docker images are tagged appropriately for each version.
4.  **Security Best Practices:** Docker images are built following security best practices.
5.  **Container Demo:** The application can be demonstrated running within a Docker container.

### Container Orchestration (Kubernetes)

1.  **Kubernetes Cluster:** The application is designed to be deployed on a Kubernetes cluster with at least two worker nodes.
2.  **Application Deployment:** The web application is deployed to the Kubernetes cluster.
3.  **Monitoring & Alerting:** Implementation for metrics, logs monitoring, and alerting for the web application.
4.  **Version Demos:**
    *   Demonstrates all three versions of the web application running in the cluster.
    *   Showcases seamless application version upgrades and rollbacks without downtime using Kubernetes rolling updates.
5.  **Monitoring & Alerting Demo:** Demonstrates the configured monitoring and alerting systems.

### CI/CD

1.  **Source Code Version Control:** The project uses Git for source code version control.
2.  **Public Code Repository:** Application files are uploaded to a public code repository (e.g., GitHub).
3.  **CI/CD Pipeline:** Implements a CI/CD pipeline to package and deploy the application to the Kubernetes cluster.
4.  **Release Process Explanation:** Provides a clear explanation of the process and steps for releasing a new application version to be deployed to the container orchestration platform.

## Project Structure

```
.dockerignore
.env.example
app.py
docker-compose.yml
Dockerfile
requirements.txt
.git/
.github/
├───workflows/
│   └───ci-cd.yml
k8s/
├───deployment.yml
├───service.yml
└───storage-class.yml
charts/
└───ant-demo/
    ├───templates/
    │   ├───deployment.yaml
    │   ├───service.yaml
    │   ├───ingressroute.yaml
    │   ├───hpa.yaml
    │   ├───pdb.yaml
    │   ├───middleware.yaml
    │   ├───serviceaccount.yaml
    │   ├───rolebinding.yaml
    │   └───_helpers.tpl
    ├───Chart.yaml
    └───values.yaml
static/
└───style.css
templates/
└───index.html
```

*   `app.py`: The main Python Flask application.
*   `Dockerfile`: Defines the Docker image for the application.
*   `requirements.txt`: Lists Python dependencies.
*   `docker-compose.yml`: For local multi-container development (if applicable).
*   `k8s/`: Contains Kubernetes deployment manifests (`deployment.yml`, `service.yml`, `storage-class.yml`).
*   `.github/workflows/ci-cd.yml`: GitHub Actions workflow for CI/CD.
*   `static/`: Static assets like CSS.
*   `templates/`: HTML templates for the Flask application.

## Getting Started

### Local Development with Docker

1.  **Build the Docker Image:**
    ```bash
    docker build -t ant-demo:v1 .
    ```
2.  **Run the Container:**
    ```bash
    docker run -p 5000:5000 ant-demo:v1
    ```
3.  Access the application at `http://localhost:5000`.

### Deployment to Kubernetes

#### Prerequisites:
*   A running Kubernetes cluster (e.g., Minikube, GKE, EKS, AKS).
*   `kubectl` configured to connect to your cluster.
*   Helm 3.x installed.
*   Traefik ingress controller deployed.

#### Deploying with Helm:
1.  **Add Traefik Helm Repository:**
    ```bash
    helm repo add traefik https://helm.traefik.io/traefik
    helm repo update
    ```

2.  **Deploy Traefik Ingress Controller:**
    ```bash
    helm install traefik traefik/traefik --namespace traefik --create-namespace \
      --set service.type=LoadBalancer \
      --set ports.web.port=80 \
      --set ports.websecure.port=443 \
      --set logs.access.enabled=true \
      --set metrics.prometheus.enabled=true
    ```

3.  **Deploy Ant Demo Application:**
    ```bash
    cd charts/ant-demo
    helm dependency update
    helm install ant-demo . --namespace ant-demo --create-namespace
    ```

4.  **Monitor Deployment:**
    ```bash
    kubectl get pods -n ant-demo
    kubectl get services -n ant-demo
    kubectl get ingressroutes -n ant-demo
    ```

5.  **Access the Application:**
    Add an entry to your `/etc/hosts` file pointing to the Traefik LoadBalancer IP:
    ```
    <TRAEFIK_EXTERNAL_IP> ant-demo.local
    ```
    
    Then access the application at `https://ant-demo.local`

#### Deploying with Traditional Manifests:
If you prefer not to use Helm, you can still use the traditional Kubernetes manifests:
```bash
kubectl apply -f k8s/
```

## CI/CD

The `.github/workflows/ci-cd.yml` file defines the CI/CD pipeline using GitHub Actions. This workflow automates the building of Docker images, tagging, pushing to a container registry, and deploying to the Kubernetes cluster upon code changes.

## Versions

This application supports three versions, each demonstrating a different feature:

*   **Version 1 (v1):** Displays "Hello World".
*   **Version 2 (v2):** Displays OS information.
*   **Version 3 (v3):** Logs access to a data storage (requires a configured database connection).

To switch between versions in Kubernetes, update the image tag in `k8s/deployment.yml` and apply the changes. Kubernetes will handle the rolling update to ensure zero downtime.