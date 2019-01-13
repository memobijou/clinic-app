from django.db.models import F
from django.urls import path, include
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


class Pagination(PageNumberPagination):
    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('data', data.get("results")),
            ("recordsTotal", data.get("records_total")),
            ("recordsFiltered", data.get("records_total")),

        ]))


class UserList(mixins.ListModelMixin, generics.GenericAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = Pagination

    def __init__(self):
        super().__init__()
        self.records_total = None

    def list(self, request, *args, **kwargs):
        print(request.GET.get("start"))
        print(request.GET.get("length"))
        print(self.queryset.count())
        

        queryset = self.filter_queryset(self.queryset)
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
