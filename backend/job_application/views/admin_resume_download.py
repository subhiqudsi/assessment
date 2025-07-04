from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.http import Http404, HttpResponse
import logging

from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.openapi import OpenApiTypes

from main.authentication import IsAdminUser

from ..models import Candidate

logger = logging.getLogger('hr_system')


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
                # Log detailed error for debugging (not exposed to client)
                logger.error(f"Error reading resume file: {str(file_error)}", exc_info=True)
                return Response({
                    'success': False,
                    'message': 'Error reading resume file'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        except Http404:
            return Response({
                'success': False,
                'message': 'Candidate not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            # Log detailed error for debugging (not exposed to client)
            logger.error(f"Resume download error: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Failed to download resume'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)