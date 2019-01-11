from django.db.models import F
from django.urls import path, include
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.decorators import action
from account.views import CreateUserView, UserListView, UserProfileView, ChangeUserPasswordView
from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets
from rest_framework.response import Response
from django.contrib.auth import views as auth_views


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

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'', UserViewSet)

urlpatterns = [
    path(r'users/api/', include(router.urls)),
    path(r'users/login/', auth_views.LoginView.as_view(), name="login"),
    path('users/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path(r'users/new/', CreateUserView.as_view(), name='create_user'),
    path(r'users/', UserListView.as_view(), name='user_list'),
    path(r'users/<int:pk>/', UserProfileView.as_view(), name='user_profile'),
    path(r'users/<int:pk>/reset-password', ChangeUserPasswordView.as_view(), name='change_user_password'),
]
