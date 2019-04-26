from django.db.models import Q
from django.db.models.functions import Lower
from django.urls import reverse_lazy

from account.models import Group
from taskmanagement.models import Task
from taskmanagement.serializers import TaskSerializer
from uniklinik.mixins import DatatablesMixin


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
        ok_span = '<span class="glyphicon glyphicon-ok text-success"></span>'
        not_ok_span = '<span class="glyphicon glyphicon-remove text-danger"></span>'

        tasks_users = query.usertasks.all()
        tasks_users_html = ""
        for query in tasks_users:
            tasks_users_html += f'<p>{query.user}&nbsp;'
            if query.completed:
                tasks_users_html += f"{ok_span}</p>"
            else:
                tasks_users_html += f"{not_ok_span}</p>"
        return tasks_users_html
