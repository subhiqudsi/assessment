# Job Application API - Swagger Documentation

This document provides information about the automated Swagger/OpenAPI documentation for the Job Application Management System.

## 📚 Documentation URLs

Once the server is running, you can access the API documentation at:

### Swagger UI (Interactive)
```
http://localhost:8000/api/docs/
```
- **Interactive documentation** with "Try it out" functionality
- Test API endpoints directly from the browser
- View request/response examples
- Authentication support

### ReDoc (Clean Documentation)
```
http://localhost:8000/api/redoc/
```
- **Clean, professional documentation** format
- Better for reading and sharing
- Print-friendly layout
- Excellent for onboarding developers

### OpenAPI Schema (Raw)
```
http://localhost:8000/api/schema/
```
- **Raw OpenAPI 3.0 specification** in YAML format
- Can be imported into other tools (Postman, Insomnia, etc.)
- Suitable for code generation tools

## 🚀 Features

### Comprehensive API Coverage
- **All endpoints documented** with detailed descriptions
- **Request/response schemas** with examples
- **Parameter documentation** with types and constraints
- **Error responses** with proper status codes

### Interactive Testing
- **Try it out functionality** in Swagger UI
- **Authentication handling** for admin endpoints
- **File upload testing** for resume endpoints
- **Real-time validation** of request data

### Rich Documentation
- **Detailed descriptions** for each endpoint
- **Authentication requirements** clearly marked
- **Business logic explanations** (file constraints, validation rules)
- **Status transition workflows** documented

## 📊 API Endpoints Overview

### Public Endpoints
| Endpoint | Method | Description | Authentication |
|----------|--------|-------------|----------------|
| `/api/info/` | GET | API information and metadata | None |
| `/api/health/` | GET | System health check | None |
| `/api/candidates/` | POST | Register new candidate | None |
| `/api/candidates/status/` | GET | Check status by email (query param) | None |
| `/api/candidates/{email}/` | GET | Check status by email (path param) | None |
| `/api/candidates/{candidate_id}/history/` | GET | Get status history | None |

### Admin Endpoints
| Endpoint | Method | Description | Authentication |
|----------|--------|-------------|----------------|
| `/api/admin/candidates/` | GET | List all candidates | X-ADMIN: 1 |
| `/api/admin/candidates/{candidate_id}/` | GET | Get candidate details | X-ADMIN: 1 |
| `/api/admin/candidates/{candidate_id}/status/` | PATCH | Update candidate status | X-ADMIN: 1 |
| `/api/admin/candidates/{candidate_id}/resume/` | GET | Download resume | X-ADMIN: 1 |

## 🔧 Technical Implementation

### drf-spectacular Configuration
The documentation is powered by `drf-spectacular`, configured in `settings.py`:

```python
SPECTACULAR_SETTINGS = {
    'TITLE': 'Job Application Management API',
    'DESCRIPTION': 'A comprehensive API for managing job applications, candidates, and HR workflows',
    'VERSION': '1.0.0',
    # ... additional configuration
}
```

### Documentation Features
- **Auto-generated** from Django REST Framework serializers and views
- **Type-safe** schema generation
- **Consistent** with actual API behavior
- **Always up-to-date** (generated from code)

### Custom Documentation
Each API view is decorated with comprehensive documentation:

```python
@extend_schema(
    operation_id='candidate_register',
    tags=['Candidates'],
    summary='Register a new job candidate',
    description='Detailed description...',
    request=CandidateRegistrationSerializer,
    responses={...},
    examples=[...]
)
```

## 📋 API Tags and Organization

### Info
- System information endpoints
- Health checks
- API metadata

### Candidates
- Public candidate-facing endpoints
- Registration and status checking
- No authentication required

### Admin
- Administrative endpoints
- Candidate management
- Requires admin authentication

## 🔐 Authentication Documentation

### Public Endpoints
- **No authentication required**
- Accessible to all users
- Rate limiting may apply

### Admin Endpoints
- **Custom header authentication**: `X-ADMIN: 1`
- Required for all administrative operations
- Clearly documented in each endpoint

## 📝 Request/Response Examples

### Registration Example
```json
{
  "full_name": "John Doe",
  "email": "john.doe@example.com",
  "phone_number": "+1234567890",
  "date_of_birth": "1990-01-01",
  "years_of_experience": 5,
  "department": "IT",
  "resume": "(binary file data)"
}
```

### Response Example
```json
{
  "success": true,
  "message": "Registration successful",
  "candidate_id": 123,
  "status": "SUBMITTED",
  "created_at": "2024-01-01T12:00:00Z"
}
```

## 🎯 Validation Documentation

### File Constraints
- **Format**: PDF or DOCX only
- **Size**: Maximum 5MB
- **Validation**: Content type and integrity checks

### Business Rules
- **Age requirement**: Candidates must be 16+ years old
- **Email uniqueness**: Each email can only be used once
- **Phone uniqueness**: Each phone number can only be used once
- **Experience range**: 0-50 years

## 🔄 Status Workflow

The documentation includes comprehensive status transition information:

```
SUBMITTED → UNDER_REVIEW → INTERVIEW_SCHEDULED → ACCEPTED/REJECTED
```

Any status can transition to `REJECTED` at any time.

## 🛠 Development Tools

### Schema Generation
Generate the OpenAPI schema file:
```bash
docker-compose exec web python manage.py spectacular --file openapi-schema.yml
```

### Import to External Tools
The generated schema can be imported into:
- **Postman** (for API testing)
- **Insomnia** (for API development)
- **Code generators** (for client SDKs)
- **API gateways** (for routing and validation)

## 📊 Monitoring and Analytics

The documentation includes information about:
- **Performance expectations** (response times)
- **Error handling** patterns
- **Logging** for audit trails
- **Monitoring** endpoints for health checks

## 🚀 Getting Started

1. **Start the server**:
   ```bash
   docker-compose up
   ```

2. **Access documentation**:
   - Visit `http://localhost:8000/api/docs/` for interactive docs
   - Visit `http://localhost:8000/api/redoc/` for clean documentation

3. **Test endpoints**:
   - Use the "Try it out" feature in Swagger UI
   - Or import the schema into your favorite API client

4. **Integrate**:
   - Download the OpenAPI schema from `/api/schema/`
   - Generate client SDKs or import into testing tools

## 🎉 Benefits

### For Developers
- **Immediate understanding** of API capabilities
- **Interactive testing** without additional tools
- **Code examples** and validation rules
- **Always up-to-date** documentation

### For Product Teams
- **Clear API specifications** for frontend development
- **Business logic documentation** for requirements
- **Error handling** documentation for UX design

### For QA Teams
- **Comprehensive test cases** from endpoint documentation
- **Validation rules** for edge case testing
- **Authentication flows** for security testing

This automated documentation system ensures that the API documentation is always accurate, comprehensive, and useful for all stakeholders.