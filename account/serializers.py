from django.db.models import Q
from rest_framework.pagination import LimitOffsetPagination

from django.contrib.auth.models import User
from rest_framework import serializers, viewsets
from account.models import Profile
from uniklinik.mixins import DatatablesMixin


class ProfileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Profile
        fields = ("is_admin", )


class UserSerializer(serializers.HyperlinkedModelSerializer):
    profile = ProfileSerializer()
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', "email", "is_superuser", "profile")


# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        self.filter_by_pk()
        return self.queryset

    def filter_by_pk(self):
        pk_filter_value = self.request.GET.get("pk")
        if pk_filter_value is not None and pk_filter_value != "":
            self.queryset = self.queryset.filter(pk=pk_filter_value)


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
        data = {"results": [[query.username, query.first_name, query.last_name, query.email] for query in page],
                "records_total": self.queryset.count()}
        return data
