from rest_framework import serializers
from ..models import Candidate


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