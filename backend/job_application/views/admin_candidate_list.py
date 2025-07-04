from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db import models
import logging

from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.openapi import OpenApiTypes

from main.authentication import IsAdminUser

from ..models import Candidate, Department, ApplicationStatus
from ..serializers import AdminCandidateListSerializer

logger = logging.getLogger('hr_system')


class CandidatePagination(PageNumberPagination):
    """Custom pagination for candidate lists"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100



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
                        'results': [
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
            return super().list(request, *args, **kwargs)
        except Exception as e:
            # Log detailed error for debugging (not exposed to client)
            logger.error(f"Admin list error: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Failed to retrieve candidates'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)