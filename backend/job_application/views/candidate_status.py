from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from django.http import Http404
import logging

from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.openapi import OpenApiTypes

from ..models import Candidate
from ..serializers import CandidateStatusSerializer

logger = logging.getLogger('hr_system')


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
    
    def get(self, request):
        """Get candidate status by ID or email"""
        email = request.query_params.get('email', None)
        try:
            # Get candidate by ID or email
            if email:
                candidate = get_object_or_404(Candidate, email=email)
            else:
                return Response({
                    'success': False,
                    'message': 'Candidate email is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
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
            # Log detailed error for debugging (not exposed to client)
            logger.error(f"Status check error: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Failed to retrieve status'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)