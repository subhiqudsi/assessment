from rest_framework import serializers
from django.core.validators import FileExtensionValidator
from ..models import Candidate, StatusHistory, ApplicationStatus
from ..validators import validate_resume_file
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

    def validate_full_name(self, value):
        """Validate full name"""
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError("Full name must be at least 2 characters long.")
        elif len(value) > 255:
            raise serializers.ValidationError("Full name is too long (maximum 255 characters).")
        elif not any(c.isalpha() for c in value):
            raise serializers.ValidationError("Full name must contain at least one letter.")
        return value

    def validate_email(self, value):
        """Custom email validation"""
        value = value.strip().lower()
        
        # Check for existing email
        if Candidate.objects.filter(email=value).exists():
            raise serializers.ValidationError("A candidate with this email already exists.")
        
        # Check length
        if len(value) > 254:  # RFC 5321 limit
            raise serializers.ValidationError("Email address is too long.")
        
        # Check for suspicious domains
        suspicious_domains = ['example.com', 'test.com', 'localhost']
        domain = value.split('@')[-1] if '@' in value else ''
        if domain in suspicious_domains:
            raise serializers.ValidationError("Please use a valid email address.")
        
        return value

    def validate_phone_number(self, value):
        """Custom phone number validation"""
        value = value.strip()
        
        # Check for existing phone number
        if Candidate.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("A candidate with this phone number already exists.")
        
        # Remove common separators for validation
        phone_digits = ''.join(c for c in value if c.isdigit())
        if len(phone_digits) < 7:
            raise serializers.ValidationError("Phone number is too short.")
        elif len(phone_digits) > 15:  # ITU-T E.164 standard
            raise serializers.ValidationError("Phone number is too long.")
        
        return value

    def validate_years_of_experience(self, value):
        """Validate years of experience"""
        if value < 0:
            raise serializers.ValidationError("Years of experience cannot be negative.")
        if value > 50:
            raise serializers.ValidationError("Years of experience cannot exceed 50.")
        return value

    def validate(self, data):
        """Cross-field validation"""
        # Validate years of experience vs age
        years_exp = data.get('years_of_experience')
        date_of_birth = data.get('date_of_birth')
        
        if years_exp is not None and date_of_birth:
            from datetime import date
            today = date.today()
            age = today.year - date_of_birth.year - (
                (today.month, today.day) < (date_of_birth.month, date_of_birth.day)
            )
            
            # Check if age is reasonable
            if age < 0 or age > 120:
                raise serializers.ValidationError({
                    'date_of_birth': f"Invalid date of birth. Calculated age: {age}"
                })
            
            # Check if years of experience is reasonable for the age
            if years_exp > 0:  # Only check if they claim experience
                max_reasonable_exp = max(0, age - 16)  # Assuming work starts at 16
                if years_exp > max_reasonable_exp:
                    raise serializers.ValidationError({
                        'years_of_experience': (
                            f"Years of experience ({years_exp}) seems unrealistic for age ({age}). "
                            f"Maximum reasonable experience would be {max_reasonable_exp} years."
                        )
                    })
        
        return data

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