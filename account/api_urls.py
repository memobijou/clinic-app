from django.urls import path, include
from rest_framework import routers
from account.serializers import UserViewSet

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'users', UserViewSet, basename="user")


urlpatterns = [
    path(r'', include(router.urls)),
]
