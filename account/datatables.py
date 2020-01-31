from django.contrib.auth.models import User
from django.db.models import Q, Case, When, Value, IntegerField
from django.urls import reverse_lazy
from account.serializers import UserSerializer, AuthorizationSerializer
from uniklinik.mixins import DatatablesMixin
from account.models import AccountAuthorization


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
                  Q(last_name__icontains=search_value) | Q(email__icontains=search_value)) |
                Q(profile__title__icontains=search_value)
            )

    def get_ordered_queryset(self):
        from django.db.models.functions import Lower
        order_column_index = self.request.GET.get("order[0][column]")
        asc_or_desc = self.request.GET.get("order[0][dir]")
        print(f"what: {order_column_index}")
        if order_column_index == "1":
            self.queryset = self.queryset.annotate(empty_title=Case(
                When(profile__title=u'', then=Value(1)),
                default=Value(0),
                output_field=IntegerField()
                )
            )
            if asc_or_desc == "asc":
                self.queryset = self.queryset.order_by("empty_title", Lower("profile__title"))
            else:
                self.queryset = self.queryset.annotate(lower_title=Lower('profile__title')).order_by(
                    "-empty_title", "-lower_title")

        elif order_column_index == "2":
            if asc_or_desc == "asc":
                self.queryset = self.queryset.order_by(Lower("first_name"))
            else:
                self.queryset = self.queryset.annotate(
                    lower_first_name=Lower("first_name")).order_by("-lower_first_name")
        elif order_column_index == "3":
            if asc_or_desc == "asc":
                self.queryset = self.queryset.order_by(Lower("last_name"))
            else:
                self.queryset = self.queryset.annotate(lower_last_name=Lower("last_name")).order_by("-lower_last_name")
        elif order_column_index == "4":
            if asc_or_desc == "asc":
                self.queryset = self.queryset.order_by(Lower("username"))
            else:
                self.queryset = self.queryset.annotate(lower_username=Lower("username")).order_by("-lower_username")
        elif order_column_index == "5":
            if asc_or_desc == "asc":
                self.queryset = self.queryset.order_by(Lower("email"))
            else:
                self.queryset = self.queryset.annotate(lower_email=Lower("email")).order_by("-lower_email")
        elif order_column_index == "6":
            if asc_or_desc == "asc":
                self.queryset = self.queryset.order_by(Lower("profile__mentor__last_name"))
            else:
                self.queryset = self.queryset.annotate(lower_mentor=Lower("profile__mentor__last_name")).order_by(
                    "-lower_mentor")
        elif order_column_index == "8":
            if asc_or_desc == "asc":
                self.queryset = self.queryset.order_by("profile__subject_area__title")
            else:
                self.queryset = self.queryset.order_by("-profile__subject_area__title")
        elif order_column_index == "9":
            if asc_or_desc == "asc":
                self.queryset = self.queryset.order_by("is_active")
            else:
                self.queryset = self.queryset.order_by("-is_active")
        return self.queryset

    def get_data(self, page):
        ok_span = '<span class="glyphicon glyphicon-ok text-success"></span>'
        not_ok_span = '<span class="glyphicon glyphicon-remove text-danger"></span>'

        data = {"results": [[
                             f'<p style="margin:0;padding:0;">'
                             f'<a href="{reverse_lazy("account:user_profile", kwargs={"pk": query.pk})}">'
                             f'Profil</a></p>'
                             f'<a href="{reverse_lazy("account:user_edit", kwargs={"pk": query.pk})}">'
                             f'Bearbeiten</a></p>'
                             f'<p style="margin:0;padding:0;"><input type="checkbox" style="cursor:pointer;" '
                             f'name="item" value={query.pk}></p>',
                             query.profile.title, query.first_name, query.last_name, query.username, query.email,
                             str(query.profile.mentor_name), query.profile.get_students_string(),
                             getattr(getattr(query.profile, "subject_area", ""), "title", ""),
                             ok_span if query.is_active is True else not_ok_span]
                            for query in page],
                "records_total": self.queryset.count()}
        return data


class AuthorizationDatatables(DatatablesMixin):
    queryset = AccountAuthorization.objects.all()
    serializer_class = AuthorizationSerializer

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
            self.queryset = self.queryset.filter(Q(Q(email__icontains=search_value)))

    def get_ordered_queryset(self):
        from django.db.models.functions import Lower
        order_column_index = self.request.GET.get("order[0][column]")
        asc_or_desc = self.request.GET.get("order[0][dir]")
        print(f"what: {order_column_index}")
        if order_column_index == "1":
            if asc_or_desc == "asc":
                self.queryset = self.queryset.order_by(Lower("email"))
            else:
                self.queryset = self.queryset.order_by(Lower("email"))
        return self.queryset

    def get_data(self, page):
        ok_span = '<span class="glyphicon glyphicon-ok text-success"></span>'
        not_ok_span = '<span class="glyphicon glyphicon-remove text-danger"></span>'

        data = {"results": [[
                             f'<p style="margin:0;padding:0;">'
                             f'<a href="{reverse_lazy("account:user_edit", kwargs={"pk": query.pk})}">'
                             f'Bearbeiten</a></p>'
                             f'<p style="margin:0;padding:0;"><input type="checkbox" style="cursor:pointer;" '
                             f'name="item" value={query.pk}></p>',
                             query.email]
                            for query in page],
                "records_total": self.queryset.count()}
        return data
