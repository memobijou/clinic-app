from django.contrib.auth.models import User
from django.db.models import Q
from django.urls import reverse_lazy

from account.serializers import UserSerializer
from uniklinik.mixins import DatatablesMixin


class UserListDatatables(DatatablesMixin):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def __init__(self):
        super().__init__()
        self.records_total = None
        self.page_number = None
        self.page_size = None

    def get_filtered_queryset(self):
        self.filter_by_search_value()
        return self.queryset

    def filter_by_search_value(self):
        search_value = self.request.GET.get("search[value]")
        if search_value != "" and search_value is not None:
            self.queryset = self.queryset.filter(
                Q(Q(username__icontains=search_value) | Q(first_name__icontains=search_value) |
                  Q(last_name__icontains=search_value) | Q(email__icontains=search_value)))

    def get_ordered_queryset(self):
        from django.db.models.functions import Lower
        order_column_index = self.request.GET.get("order[0][column]")
        asc_or_desc = self.request.GET.get("order[0][dir]")
        if order_column_index == "0":
            if asc_or_desc == "asc":
                self.queryset = self.queryset.order_by(Lower("username"))
            else:
                self.queryset = self.queryset.annotate(lower_username=Lower('username')).order_by("-lower_username")

        elif order_column_index == "1":
            if asc_or_desc == "asc":
                self.queryset = self.queryset.order_by(Lower("first_name"))
            else:
                self.queryset = self.queryset.annotate(
                    lower_first_name=Lower("first_name")).order_by("-lower_first_name")
        elif order_column_index == "2":
            if asc_or_desc == "asc":
                self.queryset = self.queryset.order_by(Lower("last_name"))
            else:
                self.queryset = self.queryset.annotate(lower_last_name=Lower("last_name")).order_by("-lower_last_name")
        elif order_column_index == "3":
            if asc_or_desc == "asc":
                self.queryset = self.queryset.order_by(Lower("email"))
            else:
                self.queryset = self.queryset.annotate(lower_email=Lower("email")).order_by("-lower_email")
        return self.queryset

    def get_data(self, page):
        ok_span = '<span class="glyphicon glyphicon-ok text-success"></span>'
        not_ok_span = '<span class="glyphicon glyphicon-remove text-danger"></span>'

        data = {"results": [[f'<input type="checkbox" style="cursor:pointer;" name="item" value={query.pk}>&nbsp&nbsp'
                             f'<a href="{reverse_lazy("account:user_edit", kwargs={"pk": query.pk})}">Bearbeiten</a>',
                             query.username, query.first_name, query.last_name, query.email,
                             str(query.profile.mentor_name), query.profile.get_students_string(),
                             getattr(getattr(query.profile, "subject_area", ""), "title", ""),
                             ok_span if query.is_active is True else not_ok_span]
                            for query in page],
                "records_total": self.queryset.count()}
        return data
