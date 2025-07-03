import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator
from datetime import date


class Department(models.TextChoices):
    IT = 'IT', 'Information Technology'
    HR = 'HR', 'Human Resources'
    FINANCE = 'FINANCE', 'Finance'


class ApplicationStatus(models.TextChoices):
    SUBMITTED = 'SUBMITTED', 'Submitted'
    UNDER_REVIEW = 'UNDER_REVIEW', 'Under Review'
    INTERVIEW_SCHEDULED = 'INTERVIEW_SCHEDULED', 'Interview Scheduled'
    REJECTED = 'REJECTED', 'Rejected'
    ACCEPTED = 'ACCEPTED', 'Accepted'


def resume_upload_path(instance, filename):
    """Generate unique file path for resume uploads"""
    # Extract file extension
    ext = filename.split('.')[-1]
    # Generate unique filename using UUID
    unique_filename = f"{uuid.uuid4()}.{ext}"
    # Return path: resumes/candidate_id/unique_filename
    return f'resumes/{instance.id}/{unique_filename}'


class Candidate(models.Model):
    """Candidate model for job applicants"""

    # Personal Information
    full_name = models.CharField(
        max_length=255,
        help_text="Candidate's full name"
    )

    email = models.EmailField(
        unique=True,
        help_text="Unique email address for the candidate"
    )

    phone_number = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique phone number for the candidate"
    )

    date_of_birth = models.DateField(
        help_text="Candidate's date of birth"
    )

    # Professional Information
    years_of_experience = models.PositiveIntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(50)
        ],
        help_text="Years of professional experience"
    )

    department = models.CharField(
        max_length=20,
        choices=Department.choices,
        help_text="Department the candidate is applying for"
    )

    # Resume File
    resume = models.FileField(
        upload_to=resume_upload_path,
        validators=[
            FileExtensionValidator(allowed_extensions=['pdf', 'docx']),
        ],
        help_text="Resume file (PDF or DOCX, max 5MB)"
    )

    # Application Status
    status = models.CharField(
        max_length=30,
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.SUBMITTED,
        help_text="Current application status"
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Registration timestamp"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last update timestamp"
    )

    class Meta:
        ordering = ['-created_at']  # Latest first
        indexes = [
            models.Index(fields=['department']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['email']),
            models.Index(fields=['phone_number']),
        ]

    def __str__(self):
        return f"{self.full_name} - {self.department}"

    def clean(self):
        """Custom validation"""
        from django.core.exceptions import ValidationError

        # Validate date of birth (candidate should be at least 16 years old)
        if self.date_of_birth:
            today = date.today()
            age = today.year - self.date_of_birth.year - (
                    (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
            if age < 16:
                raise ValidationError("Candidate must be at least 16 years old.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class StatusHistory(models.Model):
    """Track status changes for candidates"""

    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.CASCADE,
        related_name='status_history'
    )

    previous_status = models.CharField(
        max_length=30,
        choices=ApplicationStatus.choices,
        null=True,
        blank=True,
        help_text="Previous status before the change"
    )

    new_status = models.CharField(
        max_length=30,
        choices=ApplicationStatus.choices,
        help_text="New status after the change"
    )

    comments = models.TextField(
        blank=True,
        help_text="Comments or feedback for the status change"
    )

    changed_by = models.CharField(
        max_length=255,
        default='admin',
        help_text="Who made the status change"
    )

    changed_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the status was changed"
    )

    class Meta:
        ordering = ['-changed_at']
        verbose_name_plural = 'Status histories'
        indexes = [
            models.Index(fields=['candidate', '-changed_at']),
        ]

    def __str__(self):
        return f"{self.candidate.full_name}: {self.previous_status} → {self.new_status}"


class NotificationLog(models.Model):
    """Log notifications sent to candidates"""

    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.CASCADE,
        related_name='notifications'
    )

    status_change = models.ForeignKey(
        StatusHistory,
        on_delete=models.CASCADE,
        related_name='notifications'
    )

    notification_type = models.CharField(
        max_length=50,
        default='status_update',
        help_text="Type of notification sent"
    )

    sent_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the notification was sent"
    )

    success = models.BooleanField(
        default=True,
        help_text="Whether the notification was sent successfully"
    )

    error_message = models.TextField(
        blank=True,
        help_text="Error message if notification failed"
    )

    class Meta:
        ordering = ['-sent_at']
        indexes = [
            models.Index(fields=['candidate']),
            models.Index(fields=['sent_at']),
        ]

    def __str__(self):
        return f"Notification to {self.candidate.full_name} at {self.sent_at}"