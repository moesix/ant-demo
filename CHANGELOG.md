# CHANGELOG

All notable changes to this project will be documented in this file, organized by application phase following [k8s-plan.md](k8s-plan.md).

---

## [Phase 2.1] - Current Release (2026-04-25)

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

## [Phase 2.3] - Planned

### Added

- Istio service mesh integration
- mTLS between services
- Virtual services and destination rules
- Distributed tracing with Jaeger

---

## [Phase 2.4] - Planned

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