from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.db import transaction
import logging

from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiExample

from ..models import Candidate
from ..serializers import CandidateRegistrationSerializer

logger = logging.getLogger('hr_system')


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
            # Log detailed error for debugging (not exposed to client)
            logger.error(f"Registration error: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Registration failed due to server error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)