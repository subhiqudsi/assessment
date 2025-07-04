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
from ..serializers import StatusHistorySerializer

logger = logging.getLogger('hr_system')


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
            # Log detailed error for debugging (not exposed to client)
            logger.error(f"Status history error: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Failed to retrieve status history'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)