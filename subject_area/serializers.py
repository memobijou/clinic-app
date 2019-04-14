from rest_framework import serializers
from subject_area.models import SubjectArea


class SubjectAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubjectArea
        fields = ("pk", "title", )
