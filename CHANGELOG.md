# CHANGELOG

All notable changes to this project will be documented in this file, organized by application phase following [k8s-plan.md](k8s-plan.md).

---

## [Phase 2.3] - Current Release (2026-04-27)

### Added

- **CI/CD Pipeline (GitHub Actions)**:
  - Multi-service build matrix (webapp, user-service, logging-service)
  - Security scanning with Trivy (SARIF upload to GitHub Security tab)
  - Automated image push to GHCR with versioned tags
  - Conditional test execution (`skip_tests` flag)
  - Multi-architecture build preparation (linux/amd64, arm64 TBD)

- **Kubernetes Manifests**:
  - Production-grade deployments with health probes (liveness, readiness, startup)
  - Resource limits and requests for all services
  - Rolling update strategy with max surge/unavailable
  - Istio sidecar injection annotations

- **Database**:
  - PostgreSQL 16 deployment with ConfigMap init scripts
  - `logs` and `users` tables via init scripts
  - Secrets management for database credentials

- **API Routes**:
  - `/api/webapp/` route added to webapp service
  - `/api/users/` route added to user-service
  - `/api/logs/` route added to logging-service

- **DB Retry Logic**:
  - Retry `db.create_all()` on startup (30 attempts, 2s interval)
  - Graceful handling of PostgreSQL startup race conditions

### Changed

- **Dockerfile**: Removed Playwright from production image (saves ~400MB)
- **requirements.txt**: Removed playwright, pytest-playwright (test-only deps)
- **Resource requests**: App containers 100m→50m CPU, 128Mi→64Mi memory
- **Resource limits**: 500m→200m CPU, 512Mi→256Mi memory
- **Postgres resources**: 100m→50m CPU, 256Mi→128Mi memory
- **Kong → Istio**: Migrated from Kong API Gateway to Istio service mesh
- **Deployment scripts**: Updated for proper minikube workflow

### Fixed

- **CI/CD auth**: Switched from GHCR_TOKEN_RW to GITHUB_TOKEN with `packages: write`
- **Buildx input**: Fixed `dockerfile`→`file` for docker/build-push-action@v7
- **Test conditional**: Simplified build-and-push condition to avoid dependency on skipped jobs
- **Dockerfile path**: Removed explicit `file` param (defaults to `{context}/Dockerfile`)
- **ImagePullBackOff**: Fixed ghcr-creds username (moe6→moesix)
- **Readiness checks**: Updated from `1/1` to `2/2` for Istio sidecar containers
- **Verification script**: Uses port-forward instead of `kubectl exec` (slim images lack curl)
- **VirtualService routing**: Added root `/` and `/health` routes to webapp VS

### Removed

- Playwright browser binary from production Docker image
- Snyk dependency scanning (no SNYK_TOKEN available)
- Kong API Gateway configuration (replaced by Istio)

---

## [Phase 2.2] - Completed (2026-04-25)

### Added

- **Real-time Metrics Dashboard**:
  - WebSocket server using Flask-SocketIO (eventlet async)
  - Chart.js dashboard with real-time charts (50-point buffer)
  - Metrics: CPU, memory, disk, network (sent/recv)
  - Prometheus integration with custom collectors
  - Metrics endpoint at `/api/webapp/metrics`

### Changed

- **app.py**: Integrated WebSocket and Prometheus into webapp
- **requirements.txt**: Added flask-socketio, python-socketio, eventlet, prometheus_client
- **templates/index.html**: Added Chart.js dashboard with real-time updates
- **kong/kong.yml**: Added WebSocket route for /socket.io

### Fixed

- Kong route protocol validation (ws/wss not valid for HTTP routes)

---

## [Phase 2.1] - Completed (2026-04-25)

### Added

- **Kong API Gateway**: HTTP routing for all microservices
  - Declarative configuration (`kong/kong.yml`)
  - Admin API on port 8001
  - HTTP proxy on port 8000
  - gRPC proxy on port 9000
- **User Service**: Microservice for user management
  - gRPC server on port 50051
  - Flask HTTP endpoints on port 5000
  - PostgreSQL-backed data storage
- **Logging Service**: Microservice for access logging
  - gRPC server on port 50052
  - Flask HTTP endpoints on port 5000
  - PostgreSQL-backed data storage
- **Protocol buffer definitions**:
  - `user-service.proto` with CRUD operations
  - `logging-service.proto` with log operations
- **Kong Gateway API resources**:
  - `k8s/kong/gatewayclass.yaml`
  - `k8s/kong/gateway.yaml`
  - `k8s/kong/kong-routes.yaml`
- **Database initialization** (`scripts/init-db.sh`)

### Changed

- **Webapp**: Now pure UI service (removed gRPC proxy logic)
- **Docker Compose architecture**:
  - Services: webapp, user-service, logging-service, kong, postgres_db
  - Ports exposed for direct access and gateway routing
- **Kong configuration**: DB-less mode with declarative config
- **Kong routes**:
  - `/api/webapp/*` → webapp:5000
  - `/api/users/*` → user-service:5000
  - `/api/logs/*` → logging-service:5000
- **Health endpoints**: Service-specific status reporting

### Fixed

- Kong gRPC routing conflicts resolved (HTTP-only routes)
- Database connection handling for microservices

### Removed

- gRPC inter-service communication via Flask proxy
- Traefik IngressRoute configurations

---

### Added

- RabbitMQ message queue
- Message producer in Flask app
- Separate worker service
- Dead letter queue implementation

---

## [Phase 1] - v3 (2024-04-24)

### Added

- Comprehensive test suite:
  - Unit tests (`tests/test_app.py`, `tests/test_database.py`)
  - Integration tests (`tests/test_database_integration.py`)
  - E2E tests (`tests/test_e2e.py`)
- Flask-SQLAlchemy integration for database operations
- Flask-Migrate for database migration management
- PostgreSQL `access_logs` table
- Playwright for E2E testing
- Coverage reports with pytest-cov
- Documentation walkthrough (`documentation/walkthrough.md`)

### Changed

- Database connection: psycopg2.pool → Flask-SQLAlchemy
- Enhanced health endpoint with SQLAlchemy `text()` function
- Docker Compose with health check configurations

### Fixed

- Missing `access_logs` table causing test failures
- Database connection issues in health endpoint

---

## [Phase 1] - v2 (2024-04-23)

### Added

- **Version 2 - System Information**:
  - CPU usage display
  - Memory usage display
  - Disk usage display
  - Network information display
- Isonomy-inspired dark theme with glassmorphism
- Modern typography (Inter, JetBrains Mono)
- Responsive metric cards
- Animated elements (pulsing status dot, Kubernetes logo)
- Helm chart with Traefik ingress controller
- Health check endpoint with version and database status
- Kubernetes health probes (liveness, readiness, startup)
- Resource limits and requests
- Pod security context
- Topology spread constraints
- Pod Disruption Budget
- Horizontal Pod Autoscaler (HPA)
- Traefik IngressRoute with TLS
- Middleware (compression, rate limiting)
- PostgreSQL StatefulSet
- Database scripts (`scripts/db.sh`, `scripts/backup.sh`, `scripts/wait-for-db.sh`)

### Changed

- Complete HTML template redesign
- New CSS design system
- Enhanced log display with timestamps

### Removed

- Old terminal-style interface
- Legacy color scheme

### Fixed

- Mobile responsiveness at 768px breakpoints
- Semantic HTML accessibility

---

## [Phase 1] - v1 (Initial)

### Added

- Flask web application
- Version 1 ("Hello World")
- Docker containerization
- Basic Kubernetes manifests
- GitHub Actions CI/CD pipeline
- PostgreSQL integration for v3