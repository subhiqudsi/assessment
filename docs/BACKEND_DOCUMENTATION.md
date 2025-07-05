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
- **File Handling**: Secure resume upload with magic number validation
- **Status Workflow**: Complete application lifecycle management
- **Storage Abstraction**: Local filesystem with S3 migration support
- **API Documentation**: Auto-generated OpenAPI/Swagger docs
- **Logging**: Comprehensive logging with Elasticsearch integration
- **Authentication**: Header-based admin authentication system
- **Data Management**: Custom commands for populating test data
- **Validation**: Comprehensive file and data validation
- **Scalability**: Designed for 100,000+ candidate records

## Architecture

### Technology Stack

- **Framework**: Django 5.2.3 with Django REST Framework 3.16.0
- **Database**: PostgreSQL (production) / SQLite (development)
- **Storage**: Local filesystem / AWS S3 (configurable)
- **Authentication**: Header-based admin authentication (X-ADMIN: 1)
- **Documentation**: drf-spectacular for OpenAPI/Swagger
- **Logging**: Python logging with Elasticsearch handler
- **Validation**: python-magic for file type validation
- **Containerization**: Docker with docker-compose

### Project Structure

```
backend/
├── job_application/           # Main application
│   ├── models.py             # Data models
│   ├── serializers/          # DRF serializers (modular)
│   │   ├── candidate_registration_serializer.py
│   │   ├── admin_candidate_list_serializer.py
│   │   ├── admin_candidate_detail_serializer.py
│   │   ├── candidate_status_serializer.py
│   │   ├── status_history_serializer.py
│   │   ├── status_update_serializer.py
│   │   └── department_filter_serializer.py
│   ├── views/                # API views (modular)
│   │   ├── candidate_registration.py
│   │   ├── candidate_status.py
│   │   ├── candidate_status_history.py
│   │   ├── admin_candidate_list.py
│   │   ├── admin_candidate_detail.py
│   │   ├── admin_status_update.py
│   │   └── admin_resume_download.py
│   ├── validators.py         # Custom validators
│   ├── urls.py               # URL routing
│   ├── admin.py              # Django admin
│   ├── notifications.py      # Status notifications
│   ├── tests.py              # Unit tests
│   └── management/           # Custom management commands
│       └── commands/
│           ├── populate_candidates.py
│           └── init_elasticsearch.py
├── main/                     # Django project
│   ├── settings.py           # Configuration
│   ├── urls.py               # Main URL config
│   ├── authentication.py     # Custom header auth
│   ├── logging_handlers.py   # Elasticsearch logging
│   ├── views.py              # Health check
│   └── storage_backends/     # Storage abstraction
│       ├── base.py
│       ├── factory.py
│       ├── local.py
│       └── s3.py
├── media/                    # File uploads
├── logs/                     # Application logs
├── Dockerfile                # Container definition
├── docker-compose.yml        # Main services
├── docker-compose.services.yml # Support services
└── requirements.txt          # Dependencies
```

## Models

### Candidate Model

```python
class Candidate(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, unique=True)
    date_of_birth = models.DateField()
    years_of_experience = models.PositiveIntegerField()
    department = models.CharField(
        max_length=20,
        choices=Department.choices,
        default=Department.IT
    )
    resume = models.FileField(
        upload_to=resume_upload_path,
        validators=[validate_resume_file]
    )
    status = models.CharField(
        max_length=30,
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.SUBMITTED
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# Additional models
class StatusHistory(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    previous_status = models.CharField(max_length=30, null=True, blank=True)
    new_status = models.CharField(max_length=30)
    comments = models.TextField(blank=True)
    changed_by = models.CharField(max_length=255)
    changed_at = models.DateTimeField(auto_now_add=True)

class NotificationLog(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=50)
    recipient = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='sent')
```

### Choices Classes

```python
class Department(models.TextChoices):
    IT = 'IT', 'Information Technology'
    HR = 'HR', 'Human Resources'
    FINANCE = 'FINANCE', 'Finance'

class ApplicationStatus(models.TextChoices):
    SUBMITTED = 'SUBMITTED', 'Submitted'
    UNDER_REVIEW = 'UNDER_REVIEW', 'Under Review'
    INTERVIEW_SCHEDULED = 'INTERVIEW_SCHEDULED', 'Interview Scheduled'
    REJECTED = 'REJECTED', 'Rejected'
    ACCEPTED = 'ACCEPTED', 'Accepted'
```

## File Storage

### Storage Abstraction

The system implements a storage abstraction layer for easy migration between storage backends:

```python
class BaseStorage(ABC):
    @abstractmethod
    def save(self, name, content):
        """Save file content with given name"""
        pass
    
    @abstractmethod
    def url(self, name):
        """Return URL for accessing the file"""
        pass
    
    @abstractmethod
    def delete(self, name):
        """Delete the file"""
        pass
    
    @abstractmethod
    def exists(self, name):
        """Check if file exists"""
        pass

class LocalStorage(BaseStorage):
    # Local filesystem implementation
    
class S3Storage(BaseStorage):
    # AWS S3 implementation

# Factory for creating storage instances
class StorageFactory:
    @staticmethod
    def create_storage(backend_type='local'):
        if backend_type == 'local':
            return LocalStorage()
        elif backend_type == 's3':
            return S3Storage()
        else:
            raise ValueError(f"Unknown storage backend: {backend_type}")
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
STORAGE_BACKEND=local  # or s3
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
