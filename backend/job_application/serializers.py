from rest_framework import serializers
from django.core.validators import FileExtensionValidator
from .models import Candidate, StatusHistory, Department, ApplicationStatus
from .validators import validate_resume_file
import logging

logger = logging.getLogger('hr_system')


class CandidateRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for candidate registration"""

    resume = serializers.FileField(
        validators=[
            FileExtensionValidator(allowed_extensions=['pdf', 'docx']),
            validate_resume_file,
        ]
    )

    class Meta:
        model = Candidate
        fields = [
            'full_name',
            'email',
            'phone_number',
            'date_of_birth',
            'years_of_experience',
            'department',
            'resume'
        ]
        extra_kwargs = {
            'full_name': {'required': True},
            'email': {'required': True},
            'phone_number': {'required': True},
            'date_of_birth': {'required': True},
            'years_of_experience': {'required': True},
            'department': {'required': True},
            'resume': {'required': True},
        }

    def validate_email(self, value):
        """Custom email validation"""
        if Candidate.objects.filter(email=value).exists():
            raise serializers.ValidationError("A candidate with this email already exists.")
        return value

    def validate_phone_number(self, value):
        """Custom phone number validation"""
        if Candidate.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("A candidate with this phone number already exists.")
        return value

    def validate_years_of_experience(self, value):
        """Validate years of experience"""
        if value < 0:
            raise serializers.ValidationError("Years of experience cannot be negative.")
        if value > 50:
            raise serializers.ValidationError("Years of experience cannot exceed 50.")
        return value

    def create(self, validated_data):
        """Create candidate and log the registration"""
        candidate = super().create(validated_data)

        # Log registration
        logger.info(f"New candidate registered: {candidate.full_name} (ID: {candidate.id})")

        # Create initial status history
        StatusHistory.objects.create(
            candidate=candidate,
            previous_status=None,
            new_status=ApplicationStatus.SUBMITTED,
            comments="Initial application submitted",
            changed_by="system"
        )

        return candidate


class CandidateStatusSerializer(serializers.ModelSerializer):
    """Serializer for candidate status checking"""

    status_display = serializers.CharField(source='get_status_display', read_only=True)
    department_display = serializers.CharField(source='get_department_display', read_only=True)
    latest_feedback = serializers.SerializerMethodField()
    status_updated_at = serializers.SerializerMethodField()

    class Meta:
        model = Candidate
        fields = [
            'id',
            'full_name',
            'email',
            'status',
            'status_display',
            'department',
            'department_display',
            'created_at',
            'updated_at',
            'latest_feedback',
            'status_updated_at'
        ]
        read_only_fields = fields

    def get_latest_feedback(self, obj):
        """Get the latest feedback from status history"""
        latest_history = obj.status_history.first()
        return latest_history.comments if latest_history else None

    def get_status_updated_at(self, obj):
        """Get the timestamp of the latest status update"""
        latest_history = obj.status_history.first()
        return latest_history.changed_at if latest_history else obj.created_at


class StatusHistorySerializer(serializers.ModelSerializer):
    """Serializer for status history"""

    previous_status_display = serializers.CharField(source='get_previous_status_display', read_only=True)
    new_status_display = serializers.CharField(source='get_new_status_display', read_only=True)

    class Meta:
        model = StatusHistory
        fields = [
            'id',
            'previous_status',
            'previous_status_display',
            'new_status',
            'new_status_display',
            'comments',
            'changed_by',
            'changed_at'
        ]
        read_only_fields = fields


class AdminCandidateListSerializer(serializers.ModelSerializer):
    """Serializer for admin candidate list view"""

    department_display = serializers.CharField(source='get_department_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    age = serializers.SerializerMethodField()
    has_resume = serializers.SerializerMethodField()

    class Meta:
        model = Candidate
        fields = [
            'id',
            'full_name',
            'email',
            'phone_number',
            'date_of_birth',
            'age',
            'years_of_experience',
            'department',
            'department_display',
            'status',
            'status_display',
            'has_resume',
            'created_at',
            'updated_at'
        ]
        read_only_fields = fields

    def get_age(self, obj):
        """Calculate candidate's age"""
        from datetime import date
        today = date.today()
        return today.year - obj.date_of_birth.year - (
                (today.month, today.day) < (obj.date_of_birth.month, obj.date_of_birth.day)
        )

    def get_has_resume(self, obj):
        """Check if candidate has uploaded resume"""
        return bool(obj.resume)


class AdminCandidateDetailSerializer(AdminCandidateListSerializer):
    """Detailed serializer for admin candidate view"""

    status_history = StatusHistorySerializer(many=True, read_only=True)
    resume_filename = serializers.SerializerMethodField()

    class Meta(AdminCandidateListSerializer.Meta):
        fields = AdminCandidateListSerializer.Meta.fields + [
            'status_history',
            'resume_filename'
        ]

    def get_resume_filename(self, obj):
        """Get the original resume filename"""
        if obj.resume:
            return obj.resume.name.split('/')[-1]
        return None


class StatusUpdateSerializer(serializers.Serializer):
    """Serializer for updating candidate status"""

    status = serializers.ChoiceField(choices=ApplicationStatus.choices)
    comments = serializers.CharField(required=False, allow_blank=True, max_length=1000)
    changed_by = serializers.CharField(required=False, default='admin', max_length=255)

    def validate_status(self, value):
        """Validate status transition"""
        candidate = self.context.get('candidate')
        if candidate and candidate.status == value:
            raise serializers.ValidationError("Candidate is already in this status.")
        return value

    def update_status(self, candidate):
        """Update candidate status and create history record"""
        validated_data = self.validated_data
        previous_status = candidate.status
        new_status = validated_data['status']
        comments = validated_data.get('comments', '')
        changed_by = validated_data.get('changed_by', 'admin')

        # Update candidate status
        candidate.status = new_status
        candidate.save()

        # Create status history
        status_history = StatusHistory.objects.create(
            candidate=candidate,
            previous_status=previous_status,
            new_status=new_status,
            comments=comments,
            changed_by=changed_by
        )

        # Send notification to candidate
        from .notifications import send_status_update_notification
        try:
            send_status_update_notification(status_history)
        except Exception as e:
            logger.error(f"Failed to send notification for status update: {str(e)}")

        # Log status change
        logger.info(
            f"Status updated for candidate {candidate.full_name} (ID: {candidate.id}): "
            f"{previous_status} → {new_status} by {changed_by}"
        )

        return candidate, status_history


class DepartmentFilterSerializer(serializers.Serializer):
    """Serializer for department filtering"""

    department = serializers.ChoiceField(
        choices=Department.choices,
        required=False,
        allow_blank=True
    )