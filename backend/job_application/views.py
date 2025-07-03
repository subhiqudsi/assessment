from rest_framework import status, generics
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.db import transaction, models
from django.http import Http404, HttpResponse
from django.utils import timezone
import logging

from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from drf_spectacular.openapi import OpenApiTypes

from main.authentication import IsAdminUser

from .models import Candidate, StatusHistory, ApplicationStatus, Department
from .serializers import (
    CandidateRegistrationSerializer,
    CandidateStatusSerializer,
    StatusHistorySerializer,
    AdminCandidateListSerializer,
    AdminCandidateDetailSerializer,
    StatusUpdateSerializer
)
from .validators import validate_candidate_data_integrity

logger = logging.getLogger('hr_system')


class CandidatePagination(PageNumberPagination):
    """Custom pagination for candidate lists"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


@extend_schema_view(
    post=extend_schema(
        operation_id='candidate_register',
        tags=['Candidates'],
        summary='Register a new job candidate',
        description='''
        Register a new candidate for a job position. This endpoint accepts multipart/form-data 
        to handle file uploads for resumes. All fields are required.
        
        **File Requirements:**
        - Format: PDF or DOCX only
        - Size: Maximum 5MB
        - The file will be validated for format and content
        
        **Age Requirement:**
        - Candidates must be at least 16 years old
        
        **Uniqueness:**
        - Email addresses must be unique across all candidates
        - Phone numbers must be unique across all candidates
        ''',
        request=CandidateRegistrationSerializer,
        responses={
            201: OpenApiExample(
                'Success Response',
                value={
                    'success': True,
                    'message': 'Registration successful',
                    'candidate_id': 123,
                    'status': 'SUBMITTED',
                    'created_at': '2024-01-01T12:00:00Z'
                }
            ),
            400: OpenApiExample(
                'Validation Error',
                value={
                    'success': False,
                    'message': 'Validation failed',
                    'errors': {
                        'email': ['candidate with this email already exists.'],
                        'resume': ['File extension not allowed.']
                    }
                }
            )
        },
        examples=[
            OpenApiExample(
                'Complete Registration Data',
                value={
                    'full_name': 'John Doe',
                    'email': 'john.doe@example.com',
                    'phone_number': '+1234567890',
                    'date_of_birth': '1990-01-01',
                    'years_of_experience': 5,
                    'department': 'IT',
                    'resume': '(binary file data)'
                }
            )
        ]
    )
)
class CandidateRegistrationView(APIView):
    """API endpoint for candidate registration"""
    
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Register a new candidate"""
        try:
            # Validate data integrity first
            validate_candidate_data_integrity(request.data)
            
            # Create serializer with request data
            serializer = CandidateRegistrationSerializer(data=request.data)
            
            if serializer.is_valid():
                with transaction.atomic():
                    candidate = serializer.save()
                
                # Return success response
                response_data = {
                    'success': True,
                    'message': 'Registration successful',
                    'candidate_id': candidate.id,
                    'status': candidate.status,
                    'created_at': candidate.created_at
                }
                
                logger.info(f"Candidate registration successful: {candidate.full_name} (ID: {candidate.id})")
                return Response(response_data, status=status.HTTP_201_CREATED)
            
            # Return validation errors
            logger.warning(f"Registration validation failed: {serializer.errors}")
            return Response({
                'success': False,
                'message': 'Validation failed',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return Response({
                'success': False,
                'message': 'Registration failed due to server error',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema_view(
    get=extend_schema(
        operation_id='candidate_status_check',
        tags=['Candidates'],
        summary='Check candidate application status',
        description='''
        Check the status of a candidate's job application. You can check status either by:
        1. Candidate ID (in URL path)
        2. Email address (as query parameter)
        
        The response includes current status, latest feedback, and when the status was last updated.
        ''',
        parameters=[
            OpenApiParameter(
                name='email',
                description='Email address of the candidate (alternative to candidate_id)',
                required=False,
                type=OpenApiTypes.EMAIL,
                location=OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                name='candidate_id',
                description='Unique ID of the candidate',
                required=False,
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH
            )
        ],
        responses={
            200: {
                'description': 'Candidate status retrieved successfully',
                'examples': {
                    'application/json': {
                        'success': True,
                        'candidate': {
                            'id': 123,
                            'full_name': 'John Doe',
                            'email': 'john.doe@example.com',
                            'status': 'UNDER_REVIEW',
                            'status_display': 'Under Review',
                            'department': 'IT',
                            'department_display': 'Information Technology',
                            'latest_feedback': 'Application looks promising',
                            'created_at': '2024-01-01T12:00:00Z',
                            'updated_at': '2024-01-02T10:30:00Z',
                            'status_updated_at': '2024-01-02T10:30:00Z'
                        }
                    }
                }
            },
            400: {
                'description': 'Missing required parameters',
                'examples': {
                    'application/json': {
                        'success': False,
                        'message': 'Candidate ID or email is required'
                    }
                }
            },
            404: {
                'description': 'Candidate not found',
                'examples': {
                    'application/json': {
                        'success': False,
                        'message': 'Candidate not found'
                    }
                }
            }
        }
    )
)
class CandidateStatusView(APIView):
    """API endpoint for checking candidate application status"""
    
    permission_classes = [AllowAny]
    
    def get(self, request, candidate_id=None):
        """Get candidate status by ID or email"""
        try:
            # Get candidate by ID or email
            if candidate_id:
                candidate = get_object_or_404(Candidate, id=candidate_id)
            else:
                email = request.query_params.get('email')
                if not email:
                    return Response({
                        'success': False,
                        'message': 'Candidate ID or email is required'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                candidate = get_object_or_404(Candidate, email=email)
            
            # Serialize candidate data
            serializer = CandidateStatusSerializer(candidate)
            
            return Response({
                'success': True,
                'candidate': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Http404:
            return Response({
                'success': False,
                'message': 'Candidate not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Status check error: {str(e)}")
            return Response({
                'success': False,
                'message': 'Failed to retrieve status',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema_view(
    get=extend_schema(
        operation_id='candidate_status_history',
        tags=['Candidates'],
        summary='Get candidate status change history',
        description='''
        Retrieve the complete history of status changes for a specific candidate.
        Shows all status transitions with timestamps, comments, and who made the changes.
        
        History is ordered by newest changes first.
        ''',
        parameters=[
            OpenApiParameter(
                name='candidate_id',
                description='Unique ID of the candidate',
                required=True,
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH
            )
        ],
        responses={
            200: {
                'description': 'Status history retrieved successfully',
                'examples': {
                    'application/json': {
                        'success': True,
                        'candidate_id': 123,
                        'candidate_name': 'John Doe',
                        'current_status': 'UNDER_REVIEW',
                        'status_history': [
                            {
                                'id': 456,
                                'previous_status': 'SUBMITTED',
                                'previous_status_display': 'Submitted',
                                'new_status': 'UNDER_REVIEW',
                                'new_status_display': 'Under Review',
                                'comments': 'Application meets initial requirements',
                                'changed_by': 'hr_manager',
                                'changed_at': '2024-01-02T10:30:00Z'
                            },
                            {
                                'id': 455,
                                'previous_status': None,
                                'previous_status_display': None,
                                'new_status': 'SUBMITTED',
                                'new_status_display': 'Submitted',
                                'comments': 'Initial application submitted',
                                'changed_by': 'system',
                                'changed_at': '2024-01-01T12:00:00Z'
                            }
                        ]
                    }
                }
            }
        }
    )
)
class CandidateStatusHistoryView(APIView):
    """API endpoint for getting candidate status history"""
    
    permission_classes = [AllowAny]
    
    def get(self, request, candidate_id):
        """Get status history for a candidate"""
        try:
            candidate = get_object_or_404(Candidate, id=candidate_id)
            
            # Get status history
            status_history = candidate.status_history.all()
            serializer = StatusHistorySerializer(status_history, many=True)
            
            return Response({
                'success': True,
                'candidate_id': candidate.id,
                'candidate_name': candidate.full_name,
                'current_status': candidate.status,
                'status_history': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Http404:
            return Response({
                'success': False,
                'message': 'Candidate not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Status history error: {str(e)}")
            return Response({
                'success': False,
                'message': 'Failed to retrieve status history',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema_view(
    get=extend_schema(
        operation_id='admin_candidates_list',
        tags=['Admin'],
        summary='List all candidates with filtering and pagination',
        description='''
        **Admin Only**: Retrieve a paginated list of all candidates with advanced filtering options.
        
        **Authentication Required**: X-ADMIN: 1 header
        
        **Filtering Options:**
        - Department: Filter by specific department (IT, HR, FINANCE)
        - Status: Filter by application status (SUBMITTED, UNDER_REVIEW, etc.)
        - Search: Search by candidate name or email address
        
        **Pagination:**
        - Default page size: 20 candidates
        - Maximum page size: 100 candidates
        - Use `page` parameter to navigate through pages
        - Use `page_size` parameter to control items per page
        ''',
        parameters=[
            OpenApiParameter(
                name='department',
                description='Filter by department',
                required=False,
                type=OpenApiTypes.STR,
                enum=['IT', 'HR', 'FINANCE']
            ),
            OpenApiParameter(
                name='status',
                description='Filter by application status',
                required=False,
                type=OpenApiTypes.STR,
                enum=['SUBMITTED', 'UNDER_REVIEW', 'INTERVIEW_SCHEDULED', 'REJECTED', 'ACCEPTED']
            ),
            OpenApiParameter(
                name='search',
                description='Search by candidate name or email',
                required=False,
                type=OpenApiTypes.STR
            ),
            OpenApiParameter(
                name='page',
                description='Page number for pagination',
                required=False,
                type=OpenApiTypes.INT
            ),
            OpenApiParameter(
                name='page_size',
                description='Number of items per page (max 100)',
                required=False,
                type=OpenApiTypes.INT
            )
        ],
        responses={
            200: {
                'description': 'Candidates retrieved successfully',
                'examples': {
                    'application/json': {
                        'success': True,
                        'total_count': 150,
                        'candidates': [
                            {
                                'id': 123,
                                'full_name': 'John Doe',
                                'email': 'john.doe@example.com',
                                'phone_number': '+1234567890',
                                'date_of_birth': '1990-01-01',
                                'age': 34,
                                'years_of_experience': 5,
                                'department': 'IT',
                                'department_display': 'Information Technology',
                                'status': 'UNDER_REVIEW',
                                'status_display': 'Under Review',
                                'has_resume': True,
                                'created_at': '2024-01-01T12:00:00Z',
                                'updated_at': '2024-01-02T10:30:00Z'
                            }
                        ],
                        'count': 150,
                        'next': 'http://localhost:8000/api/admin/candidates/?page=2',
                        'previous': None
                    }
                }
            },
            403: {
                'description': 'Admin authentication required',
                'examples': {
                    'application/json': {
                        'error': 'Admin access required'
                    }
                }
            }
        }
    )
)
class AdminCandidateListView(generics.ListAPIView):
    """Admin endpoint to list all candidates with filtering"""
    
    queryset = Candidate.objects.all()
    serializer_class = AdminCandidateListSerializer
    permission_classes = [IsAdminUser]
    pagination_class = CandidatePagination
    
    def get_queryset(self):
        """Filter candidates based on query parameters"""
        queryset = super().get_queryset()
        
        # Filter by department
        department = self.request.query_params.get('department')
        if department and department in [choice[0] for choice in Department.choices]:
            queryset = queryset.filter(department=department)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter and status_filter in [choice[0] for choice in ApplicationStatus.choices]:
            queryset = queryset.filter(status=status_filter)
        
        # Search by name or email
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                models.Q(full_name__icontains=search) |
                models.Q(email__icontains=search)
            )
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """Custom list response format with pagination"""
        try:
            queryset = self.get_queryset()
            page = self.paginate_queryset(queryset)
            
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response({
                    'success': True,
                    'total_count': queryset.count(),
                    'candidates': serializer.data
                })
            
            # If pagination is disabled
            serializer = self.get_serializer(queryset, many=True)
            return Response({
                'success': True,
                'total_count': queryset.count(),
                'candidates': serializer.data
            })
        except Exception as e:
            logger.error(f"Admin list error: {str(e)}")
            return Response({
                'success': False,
                'message': 'Failed to retrieve candidates',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema_view(
    get=extend_schema(
        operation_id='admin_candidate_detail',
        tags=['Admin'],
        summary='Get detailed candidate information',
        description='''
        **Admin Only**: Retrieve comprehensive details about a specific candidate including:
        - All personal and professional information
        - Complete status change history
        - Resume filename information
        
        **Authentication Required**: X-ADMIN: 1 header
        ''',
        parameters=[
            OpenApiParameter(
                name='candidate_id',
                description='Unique ID of the candidate',
                required=True,
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH
            )
        ],
        responses={
            200: {
                'description': 'Candidate details retrieved successfully',
                'examples': {
                    'application/json': {
                        'success': True,
                        'candidate': {
                            'id': 123,
                            'full_name': 'John Doe',
                            'email': 'john.doe@example.com',
                            'phone_number': '+1234567890',
                            'date_of_birth': '1990-01-01',
                            'age': 34,
                            'years_of_experience': 5,
                            'department': 'IT',
                            'department_display': 'Information Technology',
                            'status': 'UNDER_REVIEW',
                            'status_display': 'Under Review',
                            'has_resume': True,
                            'resume_filename': 'john_doe_resume.pdf',
                            'created_at': '2024-01-01T12:00:00Z',
                            'updated_at': '2024-01-02T10:30:00Z',
                            'status_history': [
                                {
                                    'id': 456,
                                    'previous_status': 'SUBMITTED',
                                    'new_status': 'UNDER_REVIEW',
                                    'comments': 'Application meets requirements',
                                    'changed_by': 'hr_manager',
                                    'changed_at': '2024-01-02T10:30:00Z'
                                }
                            ]
                        }
                    }
                }
            }
        }
    )
)
class AdminCandidateDetailView(APIView):
    """Admin endpoint to get detailed candidate information"""
    
    permission_classes = [IsAdminUser]
    
    def get(self, request, candidate_id):
        """Get detailed candidate information"""
        try:
            candidate = get_object_or_404(Candidate, id=candidate_id)
            serializer = AdminCandidateDetailSerializer(candidate)
            
            return Response({
                'success': True,
                'candidate': serializer.data
            })
        except Http404:
            return Response({
                'success': False,
                'message': 'Candidate not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Admin detail error: {str(e)}")
            return Response({
                'success': False,
                'message': 'Failed to retrieve candidate details',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema_view(
    patch=extend_schema(
        operation_id='admin_update_candidate_status',
        tags=['Admin'],
        summary='Update candidate application status',
        description='''
        **Admin Only**: Update a candidate's application status with optional comments.
        
        **Authentication Required**: X-ADMIN: 1 header
        
        **Status Transitions:**
        - SUBMITTED → UNDER_REVIEW → INTERVIEW_SCHEDULED → ACCEPTED/REJECTED
        - Any status can transition to REJECTED
        
        **Automatic Actions:**
        - Creates a status history record
        - Sends notification to candidate (if configured)
        - Logs the status change
        
        **Validation:**
        - Cannot set status to the same value
        - All status values are validated against allowed choices
        ''',
        parameters=[
            OpenApiParameter(
                name='candidate_id',
                description='Unique ID of the candidate',
                required=True,
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH
            )
        ],
        request=StatusUpdateSerializer,
        responses={
            200: {
                'description': 'Status updated successfully',
                'examples': {
                    'application/json': {
                        'success': True,
                        'message': 'Status updated successfully',
                        'candidate_id': 123,
                        'previous_status': 'SUBMITTED',
                        'new_status': 'UNDER_REVIEW',
                        'updated_at': '2024-01-02T10:30:00Z'
                    }
                }
            },
            400: {
                'description': 'Validation error',
                'examples': {
                    'application/json': {
                        'success': False,
                        'message': 'Validation failed',
                        'errors': {
                            'status': ['Candidate is already in this status.']
                        }
                    }
                }
            }
        },
        examples=[
            OpenApiExample(
                'Status Update with Comments',
                value={
                    'status': 'INTERVIEW_SCHEDULED',
                    'comments': 'Interview scheduled for next Monday at 2 PM',
                    'changed_by': 'hr_manager_001'
                }
            ),
            OpenApiExample(
                'Simple Status Update',
                value={
                    'status': 'UNDER_REVIEW'
                }
            )
        ]
    )
)
class AdminStatusUpdateView(APIView):
    """Admin endpoint to update candidate status"""
    
    permission_classes = [IsAdminUser]
    
    def patch(self, request, candidate_id):
        """Update candidate status"""
        try:
            candidate = get_object_or_404(Candidate, id=candidate_id)
            
            serializer = StatusUpdateSerializer(
                data=request.data,
                context={'candidate': candidate}
            )
            
            if serializer.is_valid():
                with transaction.atomic():
                    updated_candidate, status_history = serializer.update_status(candidate)
                
                return Response({
                    'success': True,
                    'message': 'Status updated successfully',
                    'candidate_id': updated_candidate.id,
                    'previous_status': status_history.previous_status,
                    'new_status': status_history.new_status,
                    'updated_at': status_history.changed_at
                })
            
            return Response({
                'success': False,
                'message': 'Validation failed',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Http404:
            return Response({
                'success': False,
                'message': 'Candidate not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Status update error: {str(e)}")
            return Response({
                'success': False,
                'message': 'Failed to update status',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema_view(
    get=extend_schema(
        operation_id='admin_download_resume',
        tags=['Admin'],
        summary='Download candidate resume file',
        description='''
        **Admin Only**: Download the resume file for a specific candidate.
        
        **Authentication Required**: X-ADMIN: 1 header
        
        **File Information:**
        - Returns the original uploaded file (PDF or DOCX)
        - Filename includes candidate name for easy identification
        - Proper content-type headers are set for browser handling
        - Download activity is logged for audit purposes
        
        **Error Handling:**
        - Returns 404 if candidate has no resume
        - Returns 404 if file doesn't exist in storage
        - Returns 500 if file cannot be read
        ''',
        parameters=[
            OpenApiParameter(
                name='candidate_id',
                description='Unique ID of the candidate',
                required=True,
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH
            )
        ],
        responses={
            200: {
                'description': 'Resume file download',
                'content': {
                    'application/pdf': {},
                    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': {}
                }
            },
            404: {
                'description': 'Resume not found',
                'examples': {
                    'application/json': {
                        'success': False,
                        'message': 'Resume not found for this candidate'
                    }
                }
            }
        }
    )
)
class AdminResumeDownloadView(APIView):
    """Admin endpoint to download candidate resumes"""
    
    permission_classes = [IsAdminUser]
    
    def get(self, request, candidate_id):
        """Download candidate resume"""
        try:
            candidate = get_object_or_404(Candidate, id=candidate_id)
            
            if not candidate.resume:
                return Response({
                    'success': False,
                    'message': 'Resume not found for this candidate'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Check if file exists
            if not candidate.resume.storage.exists(candidate.resume.name):
                logger.error(f"Resume file not found in storage: {candidate.resume.name}")
                return Response({
                    'success': False,
                    'message': 'Resume file not found in storage'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Get file content and metadata
            try:
                file_content = candidate.resume.read()
                file_name = candidate.resume.name.split('/')[-1]
                content_type = 'application/pdf' if file_name.endswith('.pdf') else 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                
                # Log download activity
                logger.info(f"Resume downloaded for candidate {candidate.full_name} (ID: {candidate.id}) by admin")
                
                # Create HTTP response with file content
                response = HttpResponse(file_content, content_type=content_type)
                response['Content-Disposition'] = f'attachment; filename="{candidate.full_name}_resume_{file_name}"'
                response['Content-Length'] = len(file_content)
                
                return response
                
            except Exception as file_error:
                logger.error(f"Error reading resume file: {str(file_error)}")
                return Response({
                    'success': False,
                    'message': 'Error reading resume file',
                    'error': str(file_error)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        except Http404:
            return Response({
                'success': False,
                'message': 'Candidate not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Resume download error: {str(e)}")
            return Response({
                'success': False,
                'message': 'Failed to download resume',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
