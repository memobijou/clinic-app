from django.urls import path, include

from account.group.serializers import GroupDatatables, ReadOnlyGroupViewSet, UserGroupViewSet
from account.group.views import GroupListView, GroupCreateView, GroupUpdateView, GroupDeletionView
from account.viewsets import UserViewSet
from account.datatables import UserListDatatables, AuthorizationDatatables
from account.views import CreateUserView, UserListView, UserProfileView, ChangeProfilePasswordView, UserEditView, \
    UserActivationView, UserDeactivationView, UserDeletionView, ChangeUserPasswordView, CustomLoginView, \
    EmailAuthorizationView, EmailAuthorizationDeleteView
from rest_framework import routers
from django.contrib.auth import views as auth_views

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'groups', ReadOnlyGroupViewSet)
user_group_router = routers.DefaultRouter()
user_group_router.register(r'user-group', UserGroupViewSet)

urlpatterns = [
    path(r'api/', include(router.urls)),
    path(r'api/', include(user_group_router.urls)),
    path(r'users/datatables', UserListDatatables.as_view(), name="user_datatables"),
    path(r'users/authorization/datatables', AuthorizationDatatables.as_view(), name="auth_datatables"),
    path(r'groups/datatables', GroupDatatables.as_view(), name="group_datatables"),
    path(r'users/login/', CustomLoginView.as_view(), name="login"),
    path('users/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path(r'users/new/', CreateUserView.as_view(), name='create_user'),
    path(r'users/', UserListView.as_view(), name='user_list'),
    path(r'users/<int:pk>/profile', UserProfileView.as_view(), name='user_profile'),
    path(r'users/<int:pk>/edit', UserEditView.as_view(), name='user_edit'),
    path(r'users/<int:pk>/profile/reset-password', ChangeProfilePasswordView.as_view(), name='change_profile_password'),
    path(r'users/<int:pk>/reset-password', ChangeUserPasswordView.as_view(), name='change_user_password'),
    path(r'groups/', GroupListView.as_view(), name='group_list'),
    path(r'group/new/', GroupCreateView.as_view(), name='new_group'),
    path(r'group/deletion/', GroupDeletionView.as_view(), name='group_deletion'),
    path(r'group/<int:pk>/edit/', GroupUpdateView.as_view(), name='edit_group'),
    path(r'users/activation', UserActivationView.as_view(), name='user_activation'),
    path(r'users/deactivation', UserDeactivationView.as_view(), name='user_deactivation'),
    path(r'users/deletion', UserDeletionView.as_view(), name='user_deletion'),
    path(r'users/authorization', EmailAuthorizationView.as_view(), name='authorize_mail'),
    path(r'users/authorization/deletion', EmailAuthorizationDeleteView.as_view(), name='authorize_mail_deletion'),
]

