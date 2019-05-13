from django.contrib.auth.models import User
from rest_framework import serializers

from account.serializers import ProfileSerializer
from taskmanagement.models import Task, UserTask


class UserSerializer(serializers.HyperlinkedModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', "email", "is_superuser", "profile", )


class UserTaskSerializer(serializers.HyperlinkedModelSerializer):
    user = UserSerializer()

    class Meta:
        model = UserTask
        fields = ("pk", "user", "completed")


class TaskSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Task
        fields = ("pk", "name", "start_datetime", "end_datetime", "description",)


class EndUserTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTask
        fields = ("pk", "user", "task", "completed")
