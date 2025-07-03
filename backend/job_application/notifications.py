"""
Notification system for sending status updates to candidates.
This is a basic implementation that can be extended with real email/SMS providers.
"""
import logging
from typing import Optional
from django.utils import timezone
from .models import NotificationLog, StatusHistory

logger = logging.getLogger('hr_system')


class NotificationService:
    """Service for sending notifications to candidates"""
    
    def send_status_update_notification(self, status_history: StatusHistory) -> bool:
        """
        Send status update notification to candidate.
        
        Args:
            status_history: StatusHistory instance with the status change
            
        Returns:
            bool: True if notification was sent successfully, False otherwise
        """
        candidate = status_history.candidate
        
        try:
            # Generate notification message
            message = self._generate_status_message(status_history)
            
            # In a real implementation, this would send actual email/SMS
            # For now, we'll just log the notification
            self._mock_send_notification(candidate.email, message)
            
            # Log successful notification
            NotificationLog.objects.create(
                candidate=candidate,
                status_change=status_history,
                notification_type='status_update',
                success=True,
                error_message=''
            )
            
            logger.info(
                f"Status update notification sent to {candidate.full_name} "
                f"({candidate.email}) for status change: {status_history.previous_status} → {status_history.new_status}"
            )
            
            return True
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Failed to send notification to {candidate.email}: {error_msg}")
            
            # Log failed notification
            NotificationLog.objects.create(
                candidate=candidate,
                status_change=status_history,
                notification_type='status_update',
                success=False,
                error_message=error_msg
            )
            
            return False
    
    def _generate_status_message(self, status_history: StatusHistory) -> str:
        """Generate notification message based on status change"""
        candidate = status_history.candidate
        new_status = status_history.new_status
        comments = status_history.comments
        
        status_messages = {
            'SUBMITTED': f"Hello {candidate.full_name}, your application has been submitted successfully.",
            'UNDER_REVIEW': f"Hello {candidate.full_name}, your application is now under review.",
            'INTERVIEW_SCHEDULED': f"Hello {candidate.full_name}, congratulations! An interview has been scheduled for your application.",
            'REJECTED': f"Hello {candidate.full_name}, unfortunately your application was not successful this time.",
            'ACCEPTED': f"Hello {candidate.full_name}, congratulations! Your application has been accepted."
        }
        
        base_message = status_messages.get(new_status, f"Your application status has been updated to {new_status}.")
        
        if comments:
            base_message += f"\n\nAdditional feedback: {comments}"
        
        base_message += f"\n\nYou can check your application status anytime at: /api/candidates/{candidate.id}/status/"
        
        return base_message
    
    def _mock_send_notification(self, email: str, message: str) -> None:
        """
        Mock notification sending (placeholder for real implementation).
        In production, this would integrate with email/SMS providers like:
        - SendGrid, AWS SES, or Mailgun for email
        - Twilio, AWS SNS for SMS
        """
        logger.info(f"[MOCK NOTIFICATION] To: {email}")
        logger.info(f"[MOCK NOTIFICATION] Message: {message}")
        
        # Simulate potential sending failure (for testing)
        # Uncomment the line below to test error handling
        # raise Exception("Mock notification failure")


# Global notification service instance
notification_service = NotificationService()


def send_status_update_notification(status_history: StatusHistory) -> bool:
    """
    Convenience function to send status update notification.
    
    Args:
        status_history: StatusHistory instance
        
    Returns:
        bool: True if notification was sent successfully
    """
    return notification_service.send_status_update_notification(status_history)