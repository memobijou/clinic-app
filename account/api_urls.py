from django.urls import path, include
from rest_framework import routers
from account.viewsets import UserViewSet, RegistrationLoginViewset

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'users', UserViewSet, basename="user")

urlpatterns = [
    path(r'', include(router.urls)),
]
