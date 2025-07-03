# HR Management System

A complete HR system that allows job applicants to register as candidates and upload their resumes, while HR managers can log in, view the list of candidates, and download their resumes.

## 🏗️ Architecture

- **Backend**: Django REST API with PostgreSQL/SQLite support
- **Frontend**: Next.js React application with TypeScript
- **Deployment**: Kubernetes with Helm charts
- **Storage**: Local filesystem with S3 migration support
- **Containerization**: Docker with docker-compose for development

## 📁 Project Structure

```
assessment/
├── backend/                 # Django REST API
│   ├── job_application/    # Main application
│   ├── main/               # Django settings
│   ├── Dockerfile          # Backend container
│   ├── docker-compose.yml  # Development setup
│   └── requirements.txt    # Python dependencies
├── frontend/               # Next.js application
│   ├── app/               # Next.js 14 app directory
│   ├── components/        # Reusable React components
│   ├── lib/              # API client and utilities
│   ├── package.json      # Node.js dependencies
│   └── README.md         # Frontend documentation
├── helm/                  # Kubernetes deployment
│   ├── backend/          # Backend Helm chart
│   ├── frontend/         # Frontend Helm chart
│   ├── hr-system/        # Umbrella chart
│   └── README.md         # Helm documentation
├── docs/                  # Additional documentation
├── Makefile              # Build and deployment automation
└── README.md             # This file
```

## 🚀 Quick Start

### Prerequisites

- **Development**: Docker, Docker Compose, Node.js 18+
- **Production**: Kubernetes cluster, Helm 3.x
- **Optional**: Python 3.11+ for local backend development

### Local Development

```bash
# 1. Start backend services
make run

# 2. Install and start frontend
make install-frontend
make run-frontend

# 3. Access applications
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
```

### Production Deployment

```bash
# Build images
make build TAG=v1.0.0
make build-frontend TAG=v1.0.0

# Deploy to Kubernetes
make helm-apply TAG=v1.0.0

# Access via ingress
# Frontend: http://hr-system.local
# Backend: http://api.hr-system.local
```

## 📋 Makefile Commands

```
Available targets:
  build              - Build backend Docker image
  build-frontend     - Build frontend Docker image
  logs              - Show docker-compose logs
  run               - Run backend with docker-compose
  install-frontend   - Install frontend dependencies
  run-frontend       - Run frontend development server locally
  push TAG=<tag>    - Push backend image with tag

Helm Commands:
  helm-apply [TAG=<tag>]        - Deploy complete HR system (default: latest)
  helm-apply-backend [TAG=<tag>] - Deploy backend only
  helm-apply-frontend [TAG=<tag>] - Deploy frontend only
  helm-upgrade [TAG=<tag>]      - Upgrade existing deployment
  helm-delete                   - Delete all deployments
  helm-status                   - Show deployment status
  helm-template [TAG=<tag>]     - Render templates without applying

Examples:
  make helm-apply TAG=v1.0.0    - Deploy with specific image tag
  make helm-apply               - Deploy with latest tag
  make helm-upgrade TAG=v1.1.0  - Upgrade to new version
```

View all commands: `make help`

## 📚 Documentation

### Component Documentation
- **[Backend Documentation](./docs/BACKEND_DOCUMENTATION.md)** - Complete Django API reference, setup, and deployment
- **[Frontend Documentation](./frontend/README.md)** - Next.js application setup and usage
- **[Helm Documentation](./helm/README.md)** - Kubernetes deployment and configuration

### Additional Documentation
- **[API Documentation](./docs/API_DOCUMENTATION.md)** - REST API specifications and examples
- **[Populate DB Backend Guide](./docs/README_POPULATE.md)** - Backend setup and data population
- **[OpenAPI Schema](./docs/openapi-schema.yml)** - Machine-readable API specification
- **[Test Documentation](./docs/test_serializers_summary.md)** - Test serializers and validation summary
- **[Postman Collection](./docs/Job_Application_API.postman_collection.json)** - API testing collection

