from django.db.models import Q
from rest_framework.pagination import PageNumberPagination
from django.db.models.functions import Lower
from account.models import Group
from rest_framework import serializers, viewsets
from django.urls import reverse_lazy
from uniklinik.mixins import DatatablesMixin
from django.contrib.auth import get_user_model
User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('pk', 'username', 'first_name', 'last_name',)


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    users = UserSerializer(many=True)

    class Meta:
        model = Group
        fields = ("pk", 'name', "users", "color", )


class UserGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group.users.through
        fields = ("pk", 'user', "group")


# ViewSets define the view behavior.
class ReadOnlyGroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        self.filter_by_user_id()
        self.filter_by_name()
        self.filter_by_name_exact()
        self.filter_by_type()
        return self.queryset

    def filter_by_user_id(self):
        user_id = self.request.GET.get("user_id")
        if user_id:
            self.queryset = self.queryset.filter(users__id=user_id)

    def filter_by_name(self):
        name = self.request.GET.get("name")
        if name:
            self.queryset = self.queryset.filter(name__icontains=name)

    def filter_by_name_exact(self):
        name = self.request.GET.get("name_exact")
        if name:
            self.queryset = self.queryset.filter(name__iexact=name)

    def filter_by_type(self):
        type_ = self.request.GET.get("type")
        if type_:
            self.queryset = self.queryset.filter(type__iexact=type_)


# ViewSets define the view behavior.
class UserGroupViewSet(viewsets.ModelViewSet):
    queryset = Group.users.through.objects.all()
    serializer_class = UserGroupSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        user_id = self.request.GET.get("user_id")
        if user_id:
            self.queryset = self.queryset.filter(user_id=user_id)
        group_ids = self.request.GET.getlist("group_id")
        if group_ids:
            self.queryset = self.queryset.filter(group_id__in=group_ids)

        type = self.request.GET.get("type")
        if type:
            self.queryset = self.queryset.filter(group__type__iexact=type)
        return self.queryset


class GroupDatatables(DatatablesMixin):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    def __init__(self):
        super().__init__()
        self.records_total = None
        self.page_number = None
        self.page_size = None

    def get_filtered_queryset(self):
        search_value = self.request.GET.get("search[value]")
        if search_value != "" and search_value is not None:
            self.queryset = self.queryset.filter(
                Q(Q(name__icontains=search_value) | Q(users__first_name__icontains=search_value)
                  | Q(users__last_name__icontains=search_value) |
                  Q(users__profile__title__icontains=search_value))).distinct()
        return self.queryset

    def get_ordered_queryset(self):
        order_column_index = self.request.GET.get("order[0][column]")
        asc_or_desc = self.request.GET.get("order[0][dir]")
        print(f"hey: {order_column_index}")
        if order_column_index == "1":
            if asc_or_desc == "asc":
                self.queryset = self.queryset.order_by(Lower("name"))
                print(f"whyyyy: {asc_or_desc} - {order_column_index} - {self.queryset} - {Group.objects.all()}")
            else:
                self.queryset = self.queryset.annotate(lower_name=Lower('name')).order_by("-name")
        return self.queryset

    def get_data(self, page):
        data = {"results": [[f'<p><a href="'
                             f'{reverse_lazy("account:edit_group", kwargs={"pk": query.pk})}">Bearbeiten</a></p>'
                             f'<p style="margin:0;padding:0;"><input type="checkbox" style="cursor:pointer;" '
                             f'name="item" value={query.pk}></p>',
                             f'<i class="fa fa-circle" style="color:{query.color};">'
                             f'</i>&nbsp;&nbsp;<span>{query.name}</span>',
                             self.get_users(query)
                             ] for query in page],
                "records_total": self.queryset.count()}
        return data

    @staticmethod
    def get_users(query):
        users = ""
        for user in query.users.all():
            users += f"<p>{str(user)}</p>"
        return users
