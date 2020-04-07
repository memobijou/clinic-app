from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from subject_area.models import SubjectArea, Category


class SubjectAreaSerializer(serializers.ModelSerializer):
    percentage = SerializerMethodField()

    class Meta:
        model = SubjectArea
        fields = ("pk", "title", "percentage", )

    def get_percentage(self, instance):
        if self.context.get("user_id"):
            return instance.get_user_accomplishment_percentage(self.context.get("user_id"))
        else:
            return None


class CategorySerializer(serializers.ModelSerializer):
    percentage = SerializerMethodField()

    class Meta:
        model = Category
        fields = ("pk", "title", "percentage",)

    def get_percentage(self, instance: Category):
        if self.context.get("user_id"):
            return instance.get_user_accomplishment_percentage_for_category(self.context.get("user_id"))
        else:
            return None
