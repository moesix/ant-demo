# CHANGELOG

All notable changes to this project will be documented in this file.

## [Unreleased] - 2024-04-24

### Added
- Comprehensive test suite including unit, integration, and end-to-end tests
- New tests: test_app.py, test_database.py, test_database_integration.py, test_e2e.py
- Flask-SQLAlchemy integration for database operations
- Flask-Migrate for database migration management
- PostgreSQL table creation check in app.py to ensure access_logs table exists
- venv/ directory to .dockerignore for optimized Docker builds
- Playwright browsers installation in Dockerfile
- requirements.txt updates with pytest, playwright, and coverage dependencies
- Detailed walkthrough documentation in documentation/walkthrough.md

### Changed
- Updated README.md with test suite and migration information
- Modified database management section in README to use Flask-Migrate commands
- Changed db connection handling from psycopg2.pool to Flask-SQLAlchemy
- Enhanced health endpoint in app.py to use SQLAlchemy's text() function

### Fixed
- Failing test_application_rendering_and_behavior due to missing access_logs table
- Database connection issues in health endpoint

## [Unreleased] - 2024-04-23

### Added
- New Isonomy-inspired dark theme with glassmorphism effects
- Modern typography using Inter and JetBrains Mono fonts
- Responsive metric cards for system information display
- Info cards highlighting key features (Docker, Kubernetes, CI/CD)
- Animated elements (status dot pulsing, Kubernetes logo rotation)
- Comprehensive design system with CSS variables
- Helm chart with Traefik ingress controller support
- Health check endpoint (/health) with version and database status
- Kubernetes health probes (liveness, readiness, startup)
- Resource limits and requests configuration
- Pod security context and container security context
- Topology spread constraints for high availability
- Pod Disruption Budget for availability guarantees
- Horizontal Pod Autoscaler (HPA) with CPU/memory metrics
- Traefik IngressRoute with TLS and ACME support
- Middleware configurations (compression, rate limiting, redirect)
- PostgreSQL StatefulSet configuration in Helm chart
- Database initialization scripts (scripts/db.sh)
- Docker Compose health checks for both webapp and PostgreSQL
- Connection pooling for PostgreSQL using psycopg2.pool
- Database backup script (scripts/backup.sh)
- Wait-for-database script (scripts/wait-for-db.sh)

### Changed
- Complete redesign of the HTML template (templates/index.html)
- New CSS file with Isonomy design aesthetics (static/style.css)
- Updated Flask application to pass APP_VERSION to template
- Enhanced log display with timestamps and improved styling
- Added version badge and Kubernetes ready indicator
- Updated Docker Compose with health check configurations
- Updated values.yaml in Helm chart with PostgreSQL health check settings
- Enhanced app.py with connection pooling and health check improvements

### Removed
- Old terminal-style interface with green prompt and cursor animation
- Legacy color scheme and typography

### Fixed
- Improved mobile responsiveness with breakpoints at 768px
- Enhanced accessibility through semantic HTML structure