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
├── backend/                        # Django REST API
│   ├── job_application/           # Main application module
│   │   ├── management/           # Django management commands
│   │   │   └── commands/        # Custom commands (populate_candidates, init_elasticsearch)
│   │   ├── migrations/          # Database migrations
│   │   ├── serializers/         # DRF serializers (modular structure)
│   │   ├── views/              # API views (modular structure)
│   │   ├── models.py           # Data models (Candidate, StatusHistory, etc.)
│   │   ├── notifications.py    # Email notification system
│   │   ├── validators.py       # Custom validators
│   │   └── urls.py            # Application URL routing
│   ├── main/                   # Django project settings
│   │   ├── management/        # Project-level management commands
│   │   ├── storage_backends/  # Storage abstraction (local/S3)
│   │   ├── authentication.py  # Custom authentication
│   │   ├── logging_handlers.py # Elasticsearch logging handler
│   │   ├── settings.py       # Django configuration
│   │   └── urls.py          # Root URL configuration
│   ├── scripts/              # Utility scripts
│   ├── Dockerfile           # Backend container configuration
│   ├── docker-compose.yml   # Main services (Django)
│   ├── docker-compose.services.yml # Support services (PostgreSQL, Elasticsearch)
│   └── requirements.txt     # Python dependencies
├── frontend/                # Next.js application
│   ├── app/                # Next.js 14 app directory structure
│   │   ├── admin/         # Admin pages (login, dashboard)
│   │   ├── candidate/     # Candidate pages (register, status)
│   │   ├── globals.css    # Global styles
│   │   ├── layout.tsx     # Root layout
│   │   └── page.tsx       # Home page
│   ├── components/        # Reusable React components
│   │   ├── AdminDashboard.tsx
│   │   ├── CandidateForm.tsx
│   │   ├── CandidateList.tsx
│   │   ├── StatusBadge.tsx
│   │   └── StatusModal.tsx
│   ├── lib/              # Utilities and API client
│   │   ├── api.ts       # API client configuration
│   │   └── types.ts     # TypeScript type definitions
│   ├── public/          # Static assets
│   ├── Dockerfile       # Frontend container configuration
│   ├── package.json     # Node.js dependencies
│   └── README.md        # Frontend documentation
├── helm/                # Kubernetes deployment charts
│   ├── backend/        # Backend Helm chart
│   ├── frontend/       # Frontend Helm chart
│   ├── hr-system/      # Umbrella chart for full deployment
│   └── README.md       # Helm deployment guide
├── docs/               # Project documentation
│   ├── API_DOCUMENTATION.md        # API endpoints reference
│   ├── BACKEND_DOCUMENTATION.md    # Backend setup and deployment
│   ├── README_POPULATE.md          # Database population guide
│   ├── openapi-schema.yml          # OpenAPI specification
│   ├── test_serializers_summary.md # Testing documentation
│   └── Job_Application_API.postman_collection.json # Postman collection
├── init_elasticsearch.sh    # Elasticsearch index initialization script
├── Makefile                # Build and deployment automation
├── test_resume.pdf         # Test file for uploads
└── README.md              # This file
```

## 🚀 Quick Start

### Prerequisites

- **Development**: Docker, Docker Compose, Node.js 18+
- **Production**: Kubernetes cluster, Helm 3.x
- **Optional**: Python 3.11+ for local backend development

### Local Development

```bash
# 1. Build backend docker image
make build

make run-services    # Start PostgreSQL & Elasticsearch
make run-web        # Start Django application

# For the First Time Only
make init-elasticsearch
make migrate


# 2. Install and start frontend
make install-frontend
make run-frontend

# 3. Access applications
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000

# 4. Stop all services when done
make stop
```

### Production Deployment

```bash
# Build images
make build TAG=v1.0.0
make build-frontend TAG=v1.0.0

# Docker Push
docker login
make push {{TAG}}

# Deploy to Kubernetes
make helm-apply TAG=v1.0.0
```
#### TODO Adjustments are needed for serving on gunicorn and entrypoint

## 📋 Makefile Commands

```
Available targets:
  build              - Build backend Docker image
  build-frontend     - Build frontend Docker image
  logs              - Show docker-compose logs
  run               - Run all services (PostgreSQL, Elasticsearch, Django)
  run-services       - Run supporting services only (PostgreSQL, Elasticsearch)
  run-web           - Run web application only (requires services to be running)
  stop              - Stop all running services
  install-frontend   - Install frontend dependencies
  run-frontend       - Run frontend development server locally
  migrate           - Run backend database migrations
  test              - Run backend tests
  push TAG=<tag>    - Push backend image with tag

Data Management Commands:
  populate-candidates       - Create 1,000 test candidates
  populate-candidates-large - Create 100,000 test candidates
  clear-populate-candidates - Clear and create 1,000 test candidates

Django Admin Commands:
  createsuperuser    - Create Django superuser (interactive)
  shell             - Open Django shell (interactive)
  dbshell           - Open database shell (interactive)

Development Utilities:
  check             - Run Django system checks
  collectstatic     - Collect static files

Elasticsearch Commands:
  init-elasticsearch       - Initialize Elasticsearch index for logs
  init-elasticsearch-force - Force recreate Elasticsearch index

Helm Commands:
  helm-apply [TAG=<tag>]        - Deploy complete HR system (default: latest)
  helm-apply-backend [TAG=<tag>] - Deploy backend only
  helm-apply-frontend [TAG=<tag>] - Deploy frontend only
  helm-upgrade [TAG=<tag>]      - Upgrade existing deployment
  helm-delete                   - Delete all deployments
  helm-status                   - Show deployment status
  helm-template [TAG=<tag>]     - Render templates without applying

Examples:
  make run                      - Start all services for development
  make populate-candidates      - Add test data to database
  make migrate                  - Run database migrations
  make createsuperuser         - Create admin user
  make shell                   - Access Django shell
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

