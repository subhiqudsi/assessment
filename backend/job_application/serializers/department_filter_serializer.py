from rest_framework import serializers
from ..models import Department


class DepartmentFilterSerializer(serializers.Serializer):
    """Serializer for department filtering"""

    department = serializers.ChoiceField(
        choices=Department.choices,
        required=False,
        allow_blank=True
    )