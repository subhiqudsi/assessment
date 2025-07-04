from rest_framework import serializers
from .status_history_serializer import StatusHistorySerializer
from .admin_candidate_list_serializer import AdminCandidateListSerializer


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