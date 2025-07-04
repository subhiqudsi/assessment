from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from job_application.models import Candidate, Department, ApplicationStatus

from drf_spectacular.utils import extend_schema, OpenApiExample
from drf_spectacular.openapi import OpenApiTypes


@extend_schema(
    operation_id='api_info',
    tags=['Info'],
    summary='Get API information and metadata',
    description='''
    Retrieve comprehensive information about the Job Application API including:
    - Available endpoints and their paths
    - Supported departments and application statuses
    - File upload constraints and formats
    - API version information
    
    This endpoint is publicly accessible and provides essential information for API consumers.
    ''',
    responses={
        200: {
            'description': 'API information retrieved successfully',
            'examples': {
                'application/json': {
                    'version': '1.0.0',
                    'name': 'Job Application Management API',
                    'description': 'API for managing job applications and candidates',
                    'endpoints': [
                        {
                            'path': '/api/candidates/',
                            'method': 'POST',
                            'description': 'Register a new candidate'
                        },
                        {
                            'path': '/api/candidates/{id}/',
                            'method': 'GET',
                            'description': 'Check candidate status by ID'
                        }
                    ],
                    'departments': ['IT', 'HR', 'FINANCE'],
                    'statuses': ['SUBMITTED', 'UNDER_REVIEW', 'INTERVIEW_SCHEDULED', 'REJECTED', 'ACCEPTED'],
                    'file_constraints': {
                        'max_size_mb': 5,
                        'allowed_formats': ['pdf', 'docx']
                    }
                }
            }
        }
    }
)
@api_view(['GET'])
def api_info(request):
    """API information endpoint"""
    return Response({
        'version': '1.0.0',
        'name': 'Job Application Management API',
        'description': 'A comprehensive API for managing job applications, candidates, and HR workflows',
        'endpoints': [
            {
                'path': '/api/candidates/',
                'method': 'POST',
                'description': 'Register a new candidate with resume upload',
                'authentication': 'None required'
            },
            {
                'path': '/api/candidates/{id}/',
                'method': 'GET',
                'description': 'Check candidate application status by ID',
                'authentication': 'None required'
            },
            {
                'path': '/api/candidates/status/',
                'method': 'GET',
                'description': 'Check candidate application status by email',
                'authentication': 'None required'
            },
            {
                'path': '/api/candidates/{id}/history/',
                'method': 'GET',
                'description': 'Get complete status change history for a candidate',
                'authentication': 'None required'
            },
            {
                'path': '/api/admin/candidates/',
                'method': 'GET',
                'description': 'List all candidates with filtering and pagination',
                'authentication': 'Admin required (X-ADMIN: 1)'
            },
            {
                'path': '/api/admin/candidates/{id}/',
                'method': 'GET',
                'description': 'Get detailed candidate information',
                'authentication': 'Admin required (X-ADMIN: 1)'
            },
            {
                'path': '/api/admin/candidates/{id}/status/',
                'method': 'PATCH',
                'description': 'Update candidate application status',
                'authentication': 'Admin required (X-ADMIN: 1)'
            },
            {
                'path': '/api/admin/candidates/{id}/resume/',
                'method': 'GET',
                'description': 'Download candidate resume file',
                'authentication': 'Admin required (X-ADMIN: 1)'
            }
        ],
        'departments': [
            {'value': choice[0], 'display': choice[1]} 
            for choice in Department.choices
        ],
        'statuses': [
            {'value': choice[0], 'display': choice[1]} 
            for choice in ApplicationStatus.choices
        ],
        'file_constraints': {
            'max_size_mb': 5,
            'allowed_formats': ['pdf', 'docx'],
            'validation': 'Files are validated for format, size, and content integrity'
        },
        'features': [
            'Candidate registration with resume upload',
            'Status tracking and history',
            'Admin management interface',
            'Email and phone uniqueness validation',
            'Automatic notifications (when configured)',
            'Comprehensive audit logging',
            'File storage with both local and S3 support'
        ]
    })


@extend_schema(
    operation_id='health_check',
    tags=['Info'],
    summary='System health check',
    description='''
    Check the health and status of the Job Application API system including:
    - Database connectivity
    - System status
    - Basic statistics
    - Timestamp for monitoring
    
    This endpoint is useful for monitoring, alerting, and load balancer health checks.
    ''',
    responses={
        200: {
            'description': 'System is healthy',
            'examples': {
                'application/json': {
                    'status': 'ok',
                    'database_connection': 'connected',
                    'total_candidates': 1250,
                    'timestamp': '2024-01-01T12:00:00Z',
                    'version': '1.0.0',
                    'uptime_info': 'System operational'
                }
            }
        },
        503: {
            'description': 'System is unhealthy',
            'examples': {
                'application/json': {
                    'status': 'error',
                    'database_connection': 'failed',
                    'error': 'Database connection timeout',
                    'timestamp': '2024-01-01T12:00:00Z'
                }
            }
        }
    }
)
@api_view(['GET'])
def health_check(request):
    """Health check endpoint"""
    try:
        # Test database connection by counting candidates
        candidate_count = Candidate.objects.count()
        
        # Additional health checks could be added here:
        # - Cache connectivity
        # - External service availability
        # - File storage accessibility
        
        return Response({
            'status': 'ok',
            'database_connection': 'connected',
            'total_candidates': candidate_count,
            'timestamp': timezone.now(),
            'version': '1.0.0',
            'uptime_info': 'System operational'
        })
    except Exception as e:
        return Response({
            'status': 'error',
            'database_connection': 'failed',
            'error': str(e),
            'timestamp': timezone.now(),
            'version': '1.0.0'
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)