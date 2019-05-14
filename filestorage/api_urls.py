from django.urls import path
from rest_framework import routers
from filestorage.serializers import UserDirectoryViewSet
from django.urls import include


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'directories', UserDirectoryViewSet, basename="directories")


urlpatterns = [
    path(r'users/<int:user_id>/', include(router.urls)),
]
