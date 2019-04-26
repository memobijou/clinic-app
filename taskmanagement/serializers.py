from django.contrib.auth.models import User
from rest_framework import serializers, viewsets
from rest_framework.pagination import PageNumberPagination
from account.models import Group
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
    usertasks = UserTaskSerializer(many=True)

    class Meta:
        model = Task
        fields = ("pk", "name", "description", "usertasks",)


class GroupTaskSerializer(serializers.HyperlinkedModelSerializer):
    tasks = TaskSerializer(many=True)

    class Meta:
        model = Group
        fields = ("pk", 'name', "tasks", )


# ViewSets define the view behavior.
class GroupTaskViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupTaskSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        self.filter_by_group_id()
        return self.queryset

    def filter_by_group_id(self):
        group_ids = self.request.GET.getlist("group_id")

        if len(group_ids) > 0:
            groups = Group.objects.filter(pk__in=group_ids).values("pk")
            self.queryset = self.queryset.filter(pk__in=groups)


class EndUserTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTask
        fields = ("pk", "user", "task", "completed")


# ViewSets define the view behavior.
class UserTaskViewSet(viewsets.ModelViewSet):
    queryset = UserTask.objects.all()
    serializer_class = EndUserTaskSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        self.filter_by_user_id()
        self.filter_by_task_id()
        return self.queryset

    def filter_by_user_id(self):
        user_ids = self.request.GET.getlist("user_id")

        if len(user_ids) > 0:
            self.queryset = self.queryset.filter(user__id__in=user_ids)

    def filter_by_task_id(self):
        task_ids = self.request.GET.getlist("task_id")

        if len(task_ids) > 0:
            self.queryset = self.queryset.filter(task__id__in=task_ids)


