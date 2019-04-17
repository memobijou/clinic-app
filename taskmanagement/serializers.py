from django.contrib.auth.models import User
from django.db.models import Q
from django.db.models.functions import Lower
from rest_framework import serializers, viewsets
from rest_framework.pagination import PageNumberPagination
from account.models import Group
from account.serializers import ProfileSerializer
from taskmanagement.models import Task, UserTask
from uniklinik.mixins import DatatablesMixin
from django.urls import reverse_lazy


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


class TaskDatatables(DatatablesMixin):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def __init__(self):
        super().__init__()
        self.records_total = None
        self.page_number = None
        self.page_size = None

    def get_filtered_queryset(self):
        search_value = self.request.GET.get("search[value]")
        if search_value != "" and search_value is not None:
            self.queryset = self.queryset.filter(Q(name__icontains=search_value))
        return self.queryset

    def get_ordered_queryset(self):
        order_column_index = self.request.GET.get("order[1][column]")
        asc_or_desc = self.request.GET.get("order[1][dir]")
        if order_column_index == "1":
            if asc_or_desc == "asc":
                self.queryset = self.queryset.order_by(Lower("name"))
                print(f"whyyyy: {asc_or_desc} - {order_column_index} - {self.queryset} - {Group.objects.all()}")

            else:
                self.queryset = self.queryset.annotate(lower_name=Lower('name')).order_by("-name")
        return self.queryset

    def get_data(self, page):
        results = []
        for query in page:
            results.append([
                f'<p><a href="{reverse_lazy("taskmanagement:edit_task", kwargs={"pk": query.pk})}">Anzeigen</a></p>',
                query.name,
                query.description,
                self.get_groups(query),
                self.get_users(query)
            ])
        data = {"results": results,
                "records_total": self.queryset.count()}
        return data

    def get_groups(self, query):
        groups_html = ""
        for group in query.groups_list.values("name"):
            groups_html += f'<p>{group.get("name")}</p>'
        return groups_html

    def get_users(self, query):
        tasks_users = query.users.all()
        tasks_users_html = ""
        for query in tasks_users:
            tasks_users_html += f'<p>{query.first_name} {query.last_name}</p>'
        return tasks_users_html
