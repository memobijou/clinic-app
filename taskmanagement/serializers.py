from rest_framework import serializers
from django.contrib.auth.models import User
from account.serializers import ProfileSerializer
from taskmanagement.models import Task, UserTask


class UserSerializer(serializers.HyperlinkedModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', "email", "is_superuser", "profile", )


class FilteredListSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        user_id = self.context.get('user_id')
        if user_id:
            data = data.filter(user=self.context.get("user_id"))
            return data.values("completed").first()
        else:
            return data.values("user", "completed")


class UserTaskSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = UserTask
        list_serializer_class = FilteredListSerializer
        fields = ("user", "completed", )


class TaskSerializer(serializers.HyperlinkedModelSerializer):
    def to_representation(self, obj):
        primitive_repr = super().to_representation(obj)
        user_id = self.context.get("user_id")
        if user_id:
            primitive_repr['completed'] = primitive_repr['usertasks']["completed"]
            primitive_repr.pop("usertasks")
        else:
            primitive_repr['completed'] = primitive_repr['usertasks']
            primitive_repr.pop("usertasks")

        return primitive_repr

    usertasks = UserTaskSerializer(read_only=True, many=True)

    class Meta:
        model = Task
        fields = ("pk", "name", "start_datetime", "end_datetime", "description", "usertasks",)


class EndUserTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTask
        fields = ("pk", "user", "task", "completed")
