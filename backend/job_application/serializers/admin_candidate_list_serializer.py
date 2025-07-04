from rest_framework import serializers
from ..models import Candidate


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