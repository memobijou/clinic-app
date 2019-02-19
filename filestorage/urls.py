from django.urls import path
from rest_framework import routers
from filestorage.serializers import FileViewSet, FileUploadView, DirectoryViewSet
from filestorage.views import FileTreeView
from django.urls import include


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'', FileViewSet, basename="files")
directory_router = routers.DefaultRouter()

directory_router.register(r"directory", DirectoryViewSet)

urlpatterns = [
    path(r'api/', include(directory_router.urls)),

    path(r'files_api/', include(router.urls)),
    path(r'api/peform-upload/<int:directory_pk>/', FileUploadView.as_view(), name='file_upload'),
    path(r'', FileTreeView.as_view(), name="tree"),
]
