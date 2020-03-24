from django.urls import path
from rest_framework import routers
from filestorage.viewsets import UserDirectoryViewSet, ServeFileView
from django.urls import include


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'directories', UserDirectoryViewSet, basename="directories")

urlpatterns = [
    path(r'users/<int:user_id>/', include(router.urls)),
    path(r'files/<int:pk>/', ServeFileView.as_view(), name="files"),
    path(r'files/<int:pk>/users/<int:user_id>/', ServeFileView.as_view(), name="files")
]
