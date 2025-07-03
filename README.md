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
- **[Backend Documentation](./backend/README_POPULATE.md)** - Django API setup, models, and endpoints
- **[Frontend Documentation](./frontend/README.md)** - Next.js application setup and usage
- **[Helm Documentation](./helm/README.md)** - Kubernetes deployment and configuration

### Additional Documentation
- **[API Testing](./docs/)** - Test serializers and validation
- **[Deployment Guide](#deployment-summary)** - Complete deployment instructions

## 🔧 Features

### For Candidates
- ✅ **Registration**: Submit applications with personal information
- ✅ **Resume Upload**: PDF/DOCX support with 5MB size limit
- ✅ **Status Tracking**: Check application status using candidate ID
- ✅ **History View**: See status changes and feedback over time

### For HR Managers
- ✅ **Admin Dashboard**: View all candidates with filtering
- ✅ **Resume Download**: Download candidate resumes securely
- ✅ **Status Management**: Update application status with feedback
- ✅ **Department Filtering**: Filter candidates by IT, HR, Finance
- ✅ **Pagination**: Handle large numbers of applications efficiently

### Technical Features
- ✅ **Authentication**: Simple admin authentication (X-ADMIN header)
- ✅ **File Validation**: Secure file upload with type/size validation
- ✅ **API Documentation**: RESTful API with proper error handling
- ✅ **Responsive Design**: Mobile-friendly UI with Tailwind CSS
- ✅ **Containerization**: Docker support for all components
- ✅ **Kubernetes Ready**: Helm charts for production deployment
- ✅ **Storage Abstraction**: Easy migration from local to cloud storage
- ✅ **Logging**: Structured logging with Elasticsearch support
- ✅ **Scalability**: Horizontal scaling support via Kubernetes

## 🚢 Deployment Summary

### Development Environment

1. **Local Development** (Recommended for development):
   ```bash
   make run                # Backend via Docker
   make install-frontend   # Install dependencies
   make run-frontend      # Frontend dev server
   ```

2. **Full Docker** (Alternative):
   ```bash
   make build && make build-frontend
   docker-compose up -d
   ```

### Production Environment

1. **Kubernetes with Helm** (Recommended for production):
   ```bash
   # Build and tag images
   make build TAG=v1.0.0
   make build-frontend TAG=v1.0.0
   
   # Deploy to cluster
   make helm-apply TAG=v1.0.0
   
   # Monitor deployment
   make helm-status
   ```

2. **Configure DNS/Hosts**:
   ```bash
   # Add to /etc/hosts or configure DNS
   <INGRESS_IP> hr-system.local
   <INGRESS_IP> api.hr-system.local
   ```

### Environment Configuration

| Environment | Backend URL | Frontend URL | Database | Storage |
|-------------|-------------|--------------|----------|---------|
| Development | localhost:8000 | localhost:3000 | SQLite | Local |
| Production | api.hr-system.local | hr-system.local | PostgreSQL | S3/Local |

### Scaling

- **Horizontal Scaling**: Use `kubectl scale` or Helm autoscaling
- **Database**: Configure external PostgreSQL for production
- **Storage**: Migrate to S3/Azure Blob for file storage
- **Monitoring**: Enable Elasticsearch logging for observability

## 🔐 Security Considerations

- **File Upload**: Validated file types and size limits
- **Input Validation**: Server-side validation for all inputs
- **CORS**: Properly configured for cross-origin requests
- **Authentication**: Admin authentication via headers (demo only)
- **Storage**: Structured file storage with access controls

## 🧪 Testing

### Backend Testing
```bash
cd backend
python manage.py test
```

### Frontend Testing
```bash
cd frontend
npm test
```

### API Testing
```bash
# Test serializers
python backend/test_serializers.py

# Test with curl
curl -X POST http://localhost:8000/api/candidates/ \
  -F "full_name=John Doe" \
  -F "date_of_birth=1990-01-01" \
  -F "years_of_experience=5" \
  -F "department=IT" \
  -F "resume=@test_resume.pdf"
```

## 🔄 CI/CD Workflow

```bash
# 1. Development
git checkout -b feature/new-feature
make run && make run-frontend  # Local testing
git commit && git push

# 2. Build & Test
make build TAG=feature-branch
make build-frontend TAG=feature-branch

# 3. Deploy to staging
make helm-apply TAG=feature-branch

# 4. Production release
git tag v1.0.0
make build TAG=v1.0.0
make build-frontend TAG=v1.0.0
make helm-apply TAG=v1.0.0
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally with `make run` and `make run-frontend`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 📞 Support

For issues and questions:
- Check the documentation in each component's README
- Review the Makefile commands with `make help`
- Examine the Helm charts for deployment configuration

---

**Ready to get started?** Run `make help` to see all available commands!