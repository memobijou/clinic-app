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
        whole_search_value = self.request.GET.get("search[value]")
        search_values = whole_search_value.split(" ")
        for search_value in search_values:
            if search_value:
                self.queryset = self.queryset.filter(
                    Q(Q(name__icontains=search_value) | Q(description__icontains=search_value)
                      | Q(groups_list__name__icontains=search_value) |
                      Q(users__profile__title__icontains=search_value) | Q(users__first_name__icontains=search_value)
                      | Q(users__last_name__icontains=search_value))).distinct()
        return self.queryset

    def get_ordered_queryset(self):
        order_column_index = self.request.GET.get("order[0][column]")
        asc_or_desc = self.request.GET.get("order[0][dir]")
        if order_column_index == "1":
            if asc_or_desc == "asc":
                self.queryset = self.queryset.order_by(Lower("name"))
            else:
                self.queryset = self.queryset.annotate(lower_name=Lower('name')).order_by("-name")
        if order_column_index == "2":
            if asc_or_desc == "asc":
                self.queryset = self.queryset.order_by(Lower("description"))
            else:
                self.queryset = self.queryset.annotate(lower_description=Lower('description')).order_by(
                    "-lower_description")
        return self.queryset

    def get_data(self, page):
        results = []
        for query in page:
            results.append([
                f'<p style="margin:0;padding:0;"><a href='
                f'"{reverse_lazy("taskmanagement:edit_task", kwargs={"pk": query.pk})}">Anzeigen</a></p>' +
                f'<p style="margin:0;padding:0;"><input type="checkbox" style="cursor:pointer;" '
                f'name="item" value={query.pk}></p>',
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
