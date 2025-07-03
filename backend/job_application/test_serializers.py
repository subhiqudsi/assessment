import os
import tempfile
from datetime import date, datetime
from unittest.mock import patch, Mock

from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError

from .models import Candidate, StatusHistory, Department, ApplicationStatus
from .serializers import (
    CandidateRegistrationSerializer,
    CandidateStatusSerializer,
    StatusHistorySerializer,
    AdminCandidateListSerializer,
    AdminCandidateDetailSerializer,
    StatusUpdateSerializer,
    DepartmentFilterSerializer
)


class CandidateRegistrationSerializerTestCase(TestCase):
    """Test cases for CandidateRegistrationSerializer"""

    def setUp(self):
        """Set up test data"""
        self.valid_data = {
            'full_name': 'John Doe',
            'email': 'john.doe@example.com',
            'phone_number': '+1234567890',
            'date_of_birth': '1990-01-01',
            'years_of_experience': 5,
            'department': Department.IT,
        }
        # Create a test file with proper PDF header
        pdf_content = b"%PDF-1.4\n%\xE2\xE3\xCF\xD3\n"
        self.test_file = SimpleUploadedFile(
            "test_resume.pdf",
            pdf_content,
            content_type="application/pdf"
        )

    def test_valid_data_serialization(self):
        """Test serialization with valid data"""
        data = self.valid_data.copy()
        data['resume'] = self.test_file
        serializer = CandidateRegistrationSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_create_candidate(self):
        """Test candidate creation with status history"""
        data = self.valid_data.copy()
        data['resume'] = self.test_file
        serializer = CandidateRegistrationSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        with patch('job_application.serializers.logger') as mock_logger:
            candidate = serializer.save()
            
        # Check candidate was created
        self.assertEqual(candidate.full_name, 'John Doe')
        self.assertEqual(candidate.email, 'john.doe@example.com')
        self.assertEqual(candidate.status, ApplicationStatus.SUBMITTED)
        
        # Check status history was created
        history = StatusHistory.objects.filter(candidate=candidate).first()
        self.assertIsNotNone(history)
        self.assertIsNone(history.previous_status)
        self.assertEqual(history.new_status, ApplicationStatus.SUBMITTED)
        self.assertEqual(history.comments, "Initial application submitted")
        self.assertEqual(history.changed_by, "system")
        
        # Check logging was called
        mock_logger.info.assert_called_once()

    def test_duplicate_email_validation(self):
        """Test validation for duplicate email"""
        # Create existing candidate
        Candidate.objects.create(**self.valid_data, resume=self.test_file)
        
        # Try to create another with same email
        data = self.valid_data.copy()
        data['resume'] = SimpleUploadedFile("test2.pdf", b"%PDF-1.4\n", content_type="application/pdf")
        serializer = CandidateRegistrationSerializer(data=data)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)
        # Check that error message contains expected text (case-insensitive)
        error_msg = str(serializer.errors['email'][0]).lower()
        self.assertIn('email already exists', error_msg)

    def test_duplicate_phone_validation(self):
        """Test validation for duplicate phone number"""
        # Create existing candidate
        existing_data = self.valid_data.copy()
        existing_data['email'] = 'different@example.com'
        Candidate.objects.create(**existing_data, resume=self.test_file)
        
        # Try to create another with same phone
        data = self.valid_data.copy()
        data['resume'] = SimpleUploadedFile("test2.pdf", b"%PDF-1.4\n", content_type="application/pdf")
        serializer = CandidateRegistrationSerializer(data=data)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('phone_number', serializer.errors)
        # Check that error message contains expected text (case-insensitive)
        error_msg = str(serializer.errors['phone_number'][0]).lower()
        self.assertIn('phone number already exists', error_msg)

    def test_years_of_experience_validation(self):
        """Test years of experience validation"""
        # Test negative value
        data = self.valid_data.copy()
        data['years_of_experience'] = -1
        data['resume'] = SimpleUploadedFile("test.pdf", b"%PDF-1.4\n", content_type="application/pdf")
        serializer = CandidateRegistrationSerializer(data=data)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('years_of_experience', serializer.errors)
        
        # Test value > 50
        data['years_of_experience'] = 51
        data['resume'] = SimpleUploadedFile("test2.pdf", b"%PDF-1.4\n", content_type="application/pdf")
        serializer = CandidateRegistrationSerializer(data=data)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('years_of_experience', serializer.errors)

    def test_invalid_file_extension(self):
        """Test validation for invalid file extensions"""
        data = self.valid_data.copy()
        data['resume'] = SimpleUploadedFile("test.txt", b"content", content_type="text/plain")
        serializer = CandidateRegistrationSerializer(data=data)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('resume', serializer.errors)

    def test_all_fields_required(self):
        """Test that all fields are required"""
        serializer = CandidateRegistrationSerializer(data={})
        self.assertFalse(serializer.is_valid())
        
        required_fields = [
            'full_name', 'email', 'phone_number', 'date_of_birth',
            'years_of_experience', 'department', 'resume'
        ]
        for field in required_fields:
            self.assertIn(field, serializer.errors)


class CandidateStatusSerializerTestCase(TestCase):
    """Test cases for CandidateStatusSerializer"""

    def setUp(self):
        """Set up test data"""
        self.candidate = Candidate.objects.create(
            full_name='Jane Smith',
            email='jane.smith@example.com',
            phone_number='+0987654321',
            date_of_birth=date(1995, 5, 15),
            years_of_experience=3,
            department=Department.HR,
            status=ApplicationStatus.UNDER_REVIEW,
            resume=SimpleUploadedFile("resume.pdf", b"content")
        )
        
        # Create status history
        self.status_history = StatusHistory.objects.create(
            candidate=self.candidate,
            previous_status=ApplicationStatus.SUBMITTED,
            new_status=ApplicationStatus.UNDER_REVIEW,
            comments="Application looks good",
            changed_by="hr_manager"
        )

    def test_serialization(self):
        """Test candidate status serialization"""
        serializer = CandidateStatusSerializer(self.candidate)
        data = serializer.data
        
        # Check all fields
        self.assertEqual(data['id'], self.candidate.id)
        self.assertEqual(data['full_name'], 'Jane Smith')
        self.assertEqual(data['email'], 'jane.smith@example.com')
        self.assertEqual(data['status'], ApplicationStatus.UNDER_REVIEW)
        self.assertEqual(data['status_display'], 'Under Review')
        self.assertEqual(data['department'], Department.HR)
        self.assertEqual(data['department_display'], 'Human Resources')
        self.assertEqual(data['latest_feedback'], 'Application looks good')
        self.assertIsNotNone(data['status_updated_at'])

    def test_latest_feedback_none(self):
        """Test when no status history exists"""
        new_candidate = Candidate.objects.create(
            full_name='New Candidate',
            email='new@example.com',
            phone_number='+1111111111',
            date_of_birth=date(2000, 1, 1),
            years_of_experience=0,
            department=Department.FINANCE,
            resume=SimpleUploadedFile("resume.pdf", b"content")
        )
        
        serializer = CandidateStatusSerializer(new_candidate)
        data = serializer.data
        
        self.assertIsNone(data['latest_feedback'])
        # Compare as datetime objects or strings
        if isinstance(data['status_updated_at'], str):
            self.assertEqual(data['status_updated_at'], new_candidate.created_at.isoformat())
        else:
            self.assertEqual(data['status_updated_at'], new_candidate.created_at)

    def test_read_only_fields(self):
        """Test that all fields are read-only"""
        serializer = CandidateStatusSerializer(data={})
        # Since all fields are read-only, this should be valid even with empty data
        self.assertTrue(serializer.is_valid())


class StatusHistorySerializerTestCase(TestCase):
    """Test cases for StatusHistorySerializer"""

    def setUp(self):
        """Set up test data"""
        self.candidate = Candidate.objects.create(
            full_name='Test Candidate',
            email='test@example.com',
            phone_number='+1234567890',
            date_of_birth=date(1990, 1, 1),
            years_of_experience=5,
            department=Department.IT,
            resume=SimpleUploadedFile("resume.pdf", b"content")
        )
        
        self.status_history = StatusHistory.objects.create(
            candidate=self.candidate,
            previous_status=ApplicationStatus.SUBMITTED,
            new_status=ApplicationStatus.INTERVIEW_SCHEDULED,
            comments="Interview scheduled for next week",
            changed_by="recruiter"
        )

    def test_serialization(self):
        """Test status history serialization"""
        serializer = StatusHistorySerializer(self.status_history)
        data = serializer.data
        
        self.assertEqual(data['id'], self.status_history.id)
        self.assertEqual(data['previous_status'], ApplicationStatus.SUBMITTED)
        self.assertEqual(data['previous_status_display'], 'Submitted')
        self.assertEqual(data['new_status'], ApplicationStatus.INTERVIEW_SCHEDULED)
        self.assertEqual(data['new_status_display'], 'Interview Scheduled')
        self.assertEqual(data['comments'], 'Interview scheduled for next week')
        self.assertEqual(data['changed_by'], 'recruiter')
        self.assertIsNotNone(data['changed_at'])

    def test_null_previous_status(self):
        """Test serialization with null previous status"""
        history = StatusHistory.objects.create(
            candidate=self.candidate,
            previous_status=None,
            new_status=ApplicationStatus.SUBMITTED,
            comments="Initial submission",
            changed_by="system"
        )
        
        serializer = StatusHistorySerializer(history)
        data = serializer.data
        
        self.assertIsNone(data['previous_status'])
        self.assertIsNone(data['previous_status_display'])


class AdminCandidateListSerializerTestCase(TestCase):
    """Test cases for AdminCandidateListSerializer"""

    def setUp(self):
        """Set up test data"""
        self.candidate = Candidate.objects.create(
            full_name='Admin Test',
            email='admin.test@example.com',
            phone_number='+9876543210',
            date_of_birth=date(1985, 6, 15),
            years_of_experience=10,
            department=Department.FINANCE,
            resume=SimpleUploadedFile("resume.pdf", b"content")
        )

    def test_serialization(self):
        """Test admin candidate list serialization"""
        serializer = AdminCandidateListSerializer(self.candidate)
        data = serializer.data
        
        # Check all fields
        self.assertEqual(data['id'], self.candidate.id)
        self.assertEqual(data['full_name'], 'Admin Test')
        self.assertEqual(data['email'], 'admin.test@example.com')
        self.assertEqual(data['phone_number'], '+9876543210')
        self.assertEqual(str(data['date_of_birth']), '1985-06-15')
        self.assertEqual(data['years_of_experience'], 10)
        self.assertEqual(data['department'], Department.FINANCE)
        self.assertEqual(data['department_display'], 'Finance')
        self.assertEqual(data['status'], ApplicationStatus.SUBMITTED)
        self.assertEqual(data['status_display'], 'Submitted')
        self.assertTrue(data['has_resume'])

    def test_age_calculation(self):
        """Test age calculation method"""
        serializer = AdminCandidateListSerializer(self.candidate)
        data = serializer.data
        
        # Calculate expected age
        today = date.today()
        expected_age = today.year - 1985 - ((today.month, today.day) < (6, 15))
        
        self.assertEqual(data['age'], expected_age)

    def test_has_resume_false(self):
        """Test has_resume when no resume exists"""
        # Create candidate without resume (modify after creation)
        self.candidate.resume = None
        serializer = AdminCandidateListSerializer(self.candidate)
        data = serializer.data
        
        self.assertFalse(data['has_resume'])


class AdminCandidateDetailSerializerTestCase(TestCase):
    """Test cases for AdminCandidateDetailSerializer"""

    def setUp(self):
        """Set up test data"""
        self.candidate = Candidate.objects.create(
            full_name='Detail Test',
            email='detail.test@example.com',
            phone_number='+1122334455',
            date_of_birth=date(1992, 3, 20),
            years_of_experience=7,
            department=Department.IT,
            resume=SimpleUploadedFile("test_resume.pdf", b"content")
        )
        
        # Create multiple status history entries
        StatusHistory.objects.create(
            candidate=self.candidate,
            previous_status=None,
            new_status=ApplicationStatus.SUBMITTED,
            comments="Initial submission",
            changed_by="system"
        )
        StatusHistory.objects.create(
            candidate=self.candidate,
            previous_status=ApplicationStatus.SUBMITTED,
            new_status=ApplicationStatus.UNDER_REVIEW,
            comments="Reviewing application",
            changed_by="hr_team"
        )

    def test_serialization_includes_history(self):
        """Test that detail serializer includes status history"""
        serializer = AdminCandidateDetailSerializer(self.candidate)
        data = serializer.data
        
        # Check that it includes all list fields
        self.assertIn('id', data)
        self.assertIn('full_name', data)
        
        # Check additional detail fields
        self.assertIn('status_history', data)
        self.assertIn('resume_filename', data)
        
        # Check status history
        self.assertEqual(len(data['status_history']), 2)
        # History should be ordered by newest first
        self.assertEqual(
            data['status_history'][0]['new_status'],
            ApplicationStatus.UNDER_REVIEW
        )

    def test_resume_filename_extraction(self):
        """Test resume filename extraction"""
        serializer = AdminCandidateDetailSerializer(self.candidate)
        data = serializer.data
        
        # The filename should be extracted from the full path
        self.assertIn('resume_filename', data)
        self.assertIsNotNone(data['resume_filename'])

    def test_no_resume_filename(self):
        """Test when candidate has no resume"""
        self.candidate.resume = None
        serializer = AdminCandidateDetailSerializer(self.candidate)
        data = serializer.data
        
        self.assertIsNone(data['resume_filename'])


class StatusUpdateSerializerTestCase(TestCase):
    """Test cases for StatusUpdateSerializer"""

    def setUp(self):
        """Set up test data"""
        self.candidate = Candidate.objects.create(
            full_name='Status Update Test',
            email='status.update@example.com',
            phone_number='+5544332211',
            date_of_birth=date(1988, 12, 10),
            years_of_experience=12,
            department=Department.HR,
            status=ApplicationStatus.SUBMITTED,
            resume=SimpleUploadedFile("resume.pdf", b"content")
        )

    def test_valid_status_update(self):
        """Test valid status update"""
        data = {
            'status': ApplicationStatus.UNDER_REVIEW,
            'comments': 'Application being reviewed',
            'changed_by': 'hr_manager'
        }
        serializer = StatusUpdateSerializer(
            data=data,
            context={'candidate': self.candidate}
        )
        
        self.assertTrue(serializer.is_valid())

    def test_same_status_validation(self):
        """Test validation when status is unchanged"""
        data = {
            'status': ApplicationStatus.SUBMITTED,  # Same as current
            'comments': 'No change'
        }
        serializer = StatusUpdateSerializer(
            data=data,
            context={'candidate': self.candidate}
        )
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('status', serializer.errors)
        self.assertEqual(
            str(serializer.errors['status'][0]),
            "Candidate is already in this status."
        )

    @patch('job_application.notifications.send_status_update_notification')
    @patch('job_application.serializers.logger')
    def test_update_status_method(self, mock_logger, mock_send_notification):
        """Test the update_status method"""
        data = {
            'status': ApplicationStatus.INTERVIEW_SCHEDULED,
            'comments': 'Interview on Monday',
            'changed_by': 'recruiter'
        }
        serializer = StatusUpdateSerializer(
            data=data,
            context={'candidate': self.candidate}
        )
        
        self.assertTrue(serializer.is_valid())
        
        # Call update_status
        candidate, history = serializer.update_status(self.candidate)
        
        # Check candidate status was updated
        self.assertEqual(candidate.status, ApplicationStatus.INTERVIEW_SCHEDULED)
        
        # Check history was created
        self.assertEqual(history.previous_status, ApplicationStatus.SUBMITTED)
        self.assertEqual(history.new_status, ApplicationStatus.INTERVIEW_SCHEDULED)
        self.assertEqual(history.comments, 'Interview on Monday')
        self.assertEqual(history.changed_by, 'recruiter')
        
        # Check notification was attempted
        mock_send_notification.assert_called_once_with(history)
        
        # Check logging
        mock_logger.info.assert_called_once()

    @patch('job_application.notifications.send_status_update_notification')
    @patch('job_application.serializers.logger')
    def test_notification_failure_handling(self, mock_logger, mock_send_notification):
        """Test handling of notification failures"""
        # Make notification fail
        mock_send_notification.side_effect = Exception("Email service down")
        
        data = {
            'status': ApplicationStatus.REJECTED,
            'comments': 'Not suitable for position'
        }
        serializer = StatusUpdateSerializer(
            data=data,
            context={'candidate': self.candidate}
        )
        
        self.assertTrue(serializer.is_valid())
        
        # Update should still succeed even if notification fails
        candidate, history = serializer.update_status(self.candidate)
        
        # Check status was still updated
        self.assertEqual(candidate.status, ApplicationStatus.REJECTED)
        
        # Check error was logged
        mock_logger.error.assert_called_once()

    def test_optional_fields(self):
        """Test that comments and changed_by are optional"""
        data = {'status': ApplicationStatus.ACCEPTED}
        serializer = StatusUpdateSerializer(
            data=data,
            context={'candidate': self.candidate}
        )
        
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data.get('changed_by'), 'admin')
        # Comments might be None if not provided
        comments = serializer.validated_data.get('comments')
        self.assertIn(comments, ['', None])


class DepartmentFilterSerializerTestCase(TestCase):
    """Test cases for DepartmentFilterSerializer"""

    def test_valid_department(self):
        """Test serialization with valid department"""
        data = {'department': Department.IT}
        serializer = DepartmentFilterSerializer(data=data)
        
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['department'], Department.IT)

    def test_optional_department(self):
        """Test that department is optional"""
        serializer = DepartmentFilterSerializer(data={})
        self.assertTrue(serializer.is_valid())

    def test_blank_department(self):
        """Test that blank department is allowed"""
        data = {'department': ''}
        serializer = DepartmentFilterSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_invalid_department(self):
        """Test invalid department choice"""
        data = {'department': 'INVALID_DEPT'}
        serializer = DepartmentFilterSerializer(data=data)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('department', serializer.errors)