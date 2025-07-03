# HR System Backend Documentation

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Models](#models)
4. [File Storage](#file-storage)
5. [Setup and Installation](#setup-and-installation)
6. [Configuration](#configuration)
7. [Testing](#testing)
8. [Deployment](#deployment)
9. [Logging](#logging)

## Overview

The HR System backend is a Django REST Framework application that provides APIs for candidate registration, application status management, and resume handling. It supports both candidate-facing endpoints for registration and status checking, and admin-only endpoints for managing applications.

### Key Features

- **Candidate Management**: Registration, status tracking, resume upload
- **Admin Dashboard**: View candidates, download resumes, update statuses
- **File Handling**: Secure resume upload with validation
- **Status Workflow**: Complete application lifecycle management
- **Storage Abstraction**: Local filesystem with cloud migration support
- **Logging**: Comprehensive logging with Elasticsearch integration
- **Scalability**: Designed for 100,000+ candidate records

## Architecture

### Technology Stack

- **Framework**: Django 5.0+ with Django REST Framework
- **Database**: PostgreSQL (production) / SQLite (development)
- **Storage**: Local filesystem / AWS S3 (configurable)
- **Authentication**: Header-based admin authentication
- **Logging**: Python logging with Elasticsearch handler
- **Containerization**: Docker with docker-compose

### Project Structure

```
backend/
├── job_application/           # Main application
│   ├── models.py             # Data models
│   ├── serializers.py        # DRF serializers
│   ├── validators.py         # Custom validators
│   ├── views.py              # API views
│   ├── urls.py               # URL routing
│   ├── admin.py              # Django admin
│   ├── notifications.py      # Status notifications
│   ├── tests.py              # Unit tests
│   └── management/           # Custom management commands
├── main/                     # Django project
│   ├── settings.py           # Configuration
│   ├── urls.py               # Main URL config
│   ├── authentication.py     # Custom auth
│   ├── logging_handlers.py   # Custom logging
│   └── views.py              # Health check
├── media/                    # File uploads
├── logs/                     # Application logs
├── Dockerfile                # Container definition
├── docker-compose.yml        # Development setup
└── requirements.txt          # Dependencies
```

## Models

### Candidate Model

```python
class Candidate(models.Model):
    full_name = models.CharField(max_length=255)
    date_of_birth = models.DateField()
    years_of_experience = models.PositiveIntegerField()
    department = models.CharField(
        max_length=10,
        choices=[('IT', 'IT'), ('HR', 'HR'), ('Finance', 'Finance')]
    )
    resume = models.FileField(upload_to='resumes/')
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=20, default='Submitted')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### StatusHistory Model

```python
class StatusHistory(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    status = models.CharField(max_length=20)
    feedback = models.TextField(blank=True)
    changed_by = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
```

## File Storage

### Storage Abstraction

The system implements a storage abstraction layer for easy migration between storage backends:

```python
class StorageBackend:
    def save_file(self, file, path):
        pass
    
    def get_file(self, path):
        pass
    
    def delete_file(self, path):
        pass

class LocalStorageBackend(StorageBackend):
    # Local filesystem implementation
    
class S3StorageBackend(StorageBackend):
    # AWS S3 implementation
```





### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/hr_system
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=hr_system
DATABASE_USER=hr_user
DATABASE_PASSWORD=password

# Django
DEBUG=False
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1,api.hr-system.local

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://hr-system.local

# Storage
STORAGE_TYPE=local  # or s3
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_STORAGE_BUCKET_NAME=hr-system-files

# Logging
LOGGING_LEVEL=INFO
ELASTICSEARCH_HOST=localhost
ELASTICSEARCH_PORT=9200
```

## Configuration

### Database Configuration

**SQLite (Development):**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

**PostgreSQL (Production):**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DATABASE_NAME'),
        'USER': os.getenv('DATABASE_USER'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD'),
        'HOST': os.getenv('DATABASE_HOST'),
        'PORT': os.getenv('DATABASE_PORT'),
    }
}
```

### File Storage Configuration

**Local Storage:**
```python
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

**S3 Storage:**
```python
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME')
```

## Testing

### Unit Tests

```bash
# Run all tests
python manage.py test

# Run specific test
python manage.py test job_application.tests.CandidateTests

# With coverage
coverage run --source='.' manage.py test
coverage report
```

### Test Structure

```python
class CandidateTests(TestCase):
    def test_candidate_registration(self):
        # Test valid registration
        pass
    
    def test_invalid_file_upload(self):
        # Test file validation
        pass
    
    def test_status_update(self):
        # Test admin status updates
        pass
```

### API Testing

```bash
# Test with curl
curl -X POST http://localhost:8000/api/candidates/ \
  -F "full_name=John Doe" \
  -F "date_of_birth=1990-01-01" \
  -F "years_of_experience=5" \
  -F "department=IT" \
  -F "resume=@test_resume.pdf"
```

## Deployment

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

### Kubernetes Deployment

See [Helm Documentation](../helm/README.md) for complete Kubernetes deployment instructions.

```bash
# Build and deploy
make build TAG=v1.0.0
make helm-apply-backend TAG=v1.0.0
```

### Production Checklist

- [ ] Set `DEBUG=False`
- [ ] Configure production database
- [ ] Set up file storage (S3)
- [ ] Configure logging
- [ ] Set up monitoring
- [ ] Configure backup strategy
- [ ] Set up SSL/TLS
- [ ] Configure rate limiting


### File Storage Optimization

1. **CDN Integration**: Use CloudFront with S3
2. **Compression**: Compress large files before storage
3. **Caching**: Cache file metadata

### Scaling Strategies

1. **Horizontal Scaling**: Deploy multiple backend instances
2. **Database Scaling**: Read replicas for heavy read workloads
3. **Caching**: Redis for session and query caching
4. **Load Balancing**: Use NGINX or cloud load balancers





### Logging

### Configuration

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/hr_system.log',
        },
        'elasticsearch': {
            'level': 'INFO',
            'class': 'main.logging_handlers.ElasticsearchHandler',
        },
    },
    'loggers': {
        'job_application': {
            'handlers': ['file', 'elasticsearch'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

### Log Events

- User registration events
- File upload/download events
- Status change events
- Error events with stack traces
- Performance metrics

### Log Format

```json
{
    "timestamp": "2024-01-01T10:00:00Z",
    "level": "INFO",
    "event": "candidate_registered",
    "candidate_id": 123,
    "department": "IT",
    "ip_address": "192.168.1.1",
    "user_agent": "Mozilla/5.0..."
}
```



### Log Analysis

```bash
# Monitor logs in real-time
tail -f logs/hr_system.log

# Search for errors
grep -i error logs/hr_system.log

# Analyze performance
grep -i "slow" logs/hr_system.log
```
