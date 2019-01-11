from django.urls import path
from rest_framework import routers
from rest_framework import viewsets
from rest_framework.pagination import LimitOffsetPagination

from filestorage.views import FileTreeView
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status, serializers
from filestorage.models import File, FileDirectory
from django.shortcuts import get_object_or_404
from django.urls import include


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ("file", "parent_directory", "pk")

    def save(self, **kwargs):
        super().save(**kwargs)


class FileUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    queryset = File.objects.all()

    def post(self, request, *args, **kwargs):
        directory = get_object_or_404(FileDirectory, pk=self.kwargs.get("directory_pk"))
        file_serializer = FileSerializer(data=request.data)

        if file_serializer.is_valid():
            print(f"hehe: {directory.pk}")
            print(f"haha: {request.FILES}")
            file_serializer.save(parent_directory=directory, file=request.FILES.get("file"))
            return Response(file_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FileView(APIView):
    queryset = File.objects.all()

    def get_object(self, pk):
        print("123")
        return get_object_or_404(File, pk=pk)

    def delete(self, request, pk, format=None):
        print(f"456: {pk}")
        file = get_object_or_404(File, pk=self.kwargs.get("pk"))
        file.delete()
        print(f"???: {file.pk}")
        return Response(status=status.HTTP_204_NO_CONTENT)


# ViewSets define the view behavior.
class FileViewSet(viewsets.ModelViewSet):
    queryset = File.objects.all()
    serializer_class = FileSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset

    def delete(self, request, pk, format=None):
        print(f"456: {pk}")
        file = get_object_or_404(File, pk=self.kwargs.get("pk"))
        file.delete()
        print(f"???: {file.pk}")
        return Response(status=status.HTTP_204_NO_CONTENT)


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'', FileViewSet, basename="files")

urlpatterns = [
    path(r'files_api/', include(router.urls)),

    path(r'api/peform-upload/<int:directory_pk>/', FileUploadView.as_view(), name='file_upload'),

    path(r'', FileTreeView.as_view(), name="tree"),
]
