# CHANGELOG

All notable changes to this project will be documented in this file.

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

### Changed
- Complete redesign of the HTML template (templates/index.html)
- New CSS file with Isonomy design aesthetics (static/style.css)
- Updated Flask application to pass APP_VERSION to template
- Enhanced log display with timestamps and improved styling
- Added version badge and Kubernetes ready indicator

### Removed
- Old terminal-style interface with green prompt and cursor animation
- Legacy color scheme and typography

### Fixed
- Improved mobile responsiveness with breakpoints at 768px
- Enhanced accessibility through semantic HTML structure