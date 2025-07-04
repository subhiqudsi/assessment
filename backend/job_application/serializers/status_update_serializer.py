from rest_framework import serializers
from ..models import StatusHistory, ApplicationStatus
import logging

logger = logging.getLogger('hr_system')


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
        from ..notifications import send_status_update_notification
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