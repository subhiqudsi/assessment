from rest_framework import serializers
from ..models import StatusHistory


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