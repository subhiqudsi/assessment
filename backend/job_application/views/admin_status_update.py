from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.http import Http404
import logging

from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from drf_spectacular.openapi import OpenApiTypes

from main.authentication import IsAdminUser

from ..models import Candidate
from ..serializers import StatusUpdateSerializer

logger = logging.getLogger('hr_system')


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
            # Log detailed error for debugging (not exposed to client)
            logger.error(f"Status update error: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Failed to update status'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)