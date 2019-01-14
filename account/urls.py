from django.core.paginator import InvalidPage
from django.db.models import F
from django.db.models import Q
from django.urls import path, include
from rest_framework.exceptions import NotFound
from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination
from rest_framework.decorators import action
from account.views import CreateUserView, UserListView, UserProfileView, ChangeUserPasswordView
from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets
from rest_framework.response import Response
from django.contrib.auth import views as auth_views
from rest_framework import mixins
from rest_framework import generics
from collections import OrderedDict
from django.utils import six


# Serializers define the API representation.
from appointment.models import Appointment


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', "email", "is_superuser")


# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = LimitOffsetPagination


class DatatablesPagination(PageNumberPagination):
    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('data', data.get("results")),
            ("recordsTotal", data.get("records_total")),
            ("recordsFiltered", data.get("records_total")),

        ]))

    def paginate_queryset_datatables(self, queryset, page_number, page_size):
        """
        Paginate a queryset if required, either returning a
        page object, or `None` if pagination is not configured for this view.
        """

        paginator = self.django_paginator_class(queryset, page_size)

        if page_number in self.last_page_strings:
            page_number = paginator.num_pages

        try:
            page = paginator.page(page_number)
        except InvalidPage as exc:
            msg = self.invalid_page_message.format(
                page_number=page_number, message=six.text_type(exc)
            )
            raise NotFound(msg)

        if paginator.num_pages > 1 and self.template is not None:
            # The browsable API should display pagination controls.
            self.display_page_controls = True
        return list(page)


class UserList(mixins.ListModelMixin, generics.GenericAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = DatatablesPagination

    def __init__(self):
        super().__init__()
        self.records_total = None
        self.page_number = None
        self.page_size = None

    def paginate_queryset(self, queryset):
        """
        Return a single page of results, or `None` if pagination is disabled.
        """
        if self.paginator is None:
            return None
        return self.paginator.paginate_queryset_datatables(queryset,  self.page_number, self.page_size)

    def list(self, request, *args, **kwargs):
        print(request.GET.get("start"))
        print(request.GET.get("length"))
        print(self.queryset.count())
        start = int(request.GET.get("start"))
        length = int(request.GET.get("length"))
        page_number = 1
        while start > 0:
            start -= length
            page_number += 1
            if start == 0:
                break

        self.page_number = page_number
        self.page_size = length

        print(f"Page: {page_number}")
        queryset = self.filter_queryset(self.queryset)
        queryset = self.get_filtered_queryset()
        queryset = self.get_ordered_queryset()
        page = self.paginate_queryset(queryset)
        print(f"haack: {page}")
        if page is not None:
            data = {"results": [[query.username, query.first_name, query.last_name, query.email] for query in page],
                    "records_total": self.queryset.count()}

            return self.get_paginated_response(data)
        # hier checken was passiert wenn der queryset leer ist !
        serializer = self.get_serializer(queryset, many=True)
        print(f"???: {serializer.data}")
        return Response(serializer.data)

    def get_filtered_queryset(self):
        search_value = self.request.GET.get("search[value]")
        if search_value != "" and search_value is not None:
            self.queryset = self.queryset.filter(
                Q(Q(username__icontains=search_value) | Q(first_name__icontains=search_value) |
                  Q(last_name__icontains=search_value) | Q(email__icontains=search_value)))
        return self.queryset

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

    def get(self, request, *args, **kwargs):
        response = self.list(request, *args, **kwargs)
        print(response)
        return response

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'', UserViewSet)

urlpatterns = [
    path(r'users/api/', include(router.urls)),
    path(r'users/datatables', UserList.as_view()),
    path(r'users/login/', auth_views.LoginView.as_view(), name="login"),
    path('users/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path(r'users/new/', CreateUserView.as_view(), name='create_user'),
    path(r'users/', UserListView.as_view(), name='user_list'),
    path(r'users/<int:pk>/', UserProfileView.as_view(), name='user_profile'),
    path(r'users/<int:pk>/reset-password', ChangeUserPasswordView.as_view(), name='change_user_password'),
]
