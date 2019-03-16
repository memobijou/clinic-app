from django.urls import path
from rest_framework import routers
from filestorage.serializers import FileViewSet, FileUploadCreateView, DirectoryViewSet, FileUploadUpdateView
from filestorage.views import FileDirectoryView, DownloadView
from django.urls import include
from filestorage.views import FileView


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'', FileViewSet, basename="files")
directory_router = routers.DefaultRouter()

directory_router.register(r"directory", DirectoryViewSet)

urlpatterns = [
    path(r'api/', include(directory_router.urls)),

    path(r'files_api/', include(router.urls)),
    path(r'api/peform-upload/<int:directory_pk>/', FileUploadCreateView.as_view(), name='file_upload'),
    path(r'api/file/<int:file_pk>/edit/', FileUploadUpdateView.as_view(), name="file_upload_edit"),
    path(r'', FileDirectoryView.as_view(), name="tree"),
    path(r'downloads/', DownloadView.as_view(), name="download"),
    path(r'file/<int:pk>/', FileView.as_view(), name="file")

]
