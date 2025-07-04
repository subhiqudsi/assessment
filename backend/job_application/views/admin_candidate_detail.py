from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.http import Http404
import logging

from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.openapi import OpenApiTypes

from main.authentication import IsAdminUser

from ..models import Candidate
from ..serializers import AdminCandidateDetailSerializer

logger = logging.getLogger('hr_system')


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
            # Log detailed error for debugging (not exposed to client)
            logger.error(f"Admin detail error: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Failed to retrieve candidate details'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)