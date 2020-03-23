from _pydecimal import Decimal
from abc import ABCMeta, abstractmethod
from django.db.models import Sum, Q
from django.db.models.functions import Coalesce
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework import mixins, viewsets, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView

from filestorage.models import FileDirectory, FileUserHistory, File
from filestorage.serializers import FileDirectorySerializer, FileSerializer, FileUpdateSerializer, \
    send_file_messages_through_firebase


class UserDirectoryViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = FileDirectory.objects.all()
    serializer_class = FileDirectorySerializer
    pagination_class = PageNumberPagination

    def get_serializer_context(self):
        return {"request": self.request, "user_id": self.kwargs.get("user_id")}

    def get_queryset(self):
        self.queryset = super().get_queryset()
        directory_id = self.kwargs.get("pk")
        user_id = self.kwargs.get("user_id")

        if not directory_id:
            self.queryset = self.queryset.filter(parent__isnull=True)
        self.filter_by_name()
        self.filter_by_name_exact()

        if self.kwargs.get("user_id"):
            user = get_object_or_404(User, pk=user_id)
            user.profile.filestorage_badges = 0
            user.profile.save()

        if directory_id:
            FileUserHistory.objects.filter(user_id=user_id, file__parent_directory_id=directory_id).distinct().update(
             unread_notifications=0)

        return self.queryset

    def filter_by_name(self):
        name = self.request.GET.get("name")
        if name is not None:
            self.queryset = self.queryset.filter(name__icontains=name)

    def filter_by_name_exact(self):
        name = self.request.GET.get("name_exact")
        if name is not None:
            self.queryset = self.queryset.filter(name__iexact=name)


class FileViewSet(viewsets.ModelViewSet):
    queryset = File.objects.all()
    serializer_class = FileSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset

    def delete(self, request, pk, format=None):
        print(f"456: {pk}")
        file = get_object_or_404(File, pk=self.kwargs.get("pk"))
        file.delete()
        print(f"???: {file.pk}")
        return Response(status=status.HTTP_204_NO_CONTENT)


class IFileUploadView(APIView, metaclass=ABCMeta):
    parser_classes = (MultiPartParser, FormParser)
    queryset = File.objects.all()

    @abstractmethod
    def post(self, request, *args, **kwargs):
        pass


class FileUploadCreateView(IFileUploadView):
    directory = None

    def post(self, request, *args, **kwargs):
        self.directory = get_object_or_404(FileDirectory, pk=self.kwargs.get("directory_pk"))
        file_serializer = FileSerializer(data=request.data)

        if file_serializer.is_valid():
            print(f"hehe: {self.directory.pk}")
            print(f"haha: {request.FILES}")
            file_serializer.save(parent_directory=self.directory, file=request.FILES.get("file"))
            return Response(file_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FileUploadUpdateView(IFileUploadView):
    file = None

    def post(self, request, *args, **kwargs):
        self.file = get_object_or_404(File, pk=self.kwargs.get("file_pk"))
        origin_file = self.file.file
        data = request.data
        version = self.request.POST.get("version")
        name = self.request.POST.get("name")

        if not version:
            self.file.version += Decimal(0.01)

        file_serializer = FileUpdateSerializer(data=data, instance=self.file)

        if file_serializer.is_valid():
            origin_file.delete()
            version = request.POST.get("version")

            if version:
                self.file.version = version
            self.file.file = request.FILES.get("file")

            if name:
                self.file.file.name = name

            self.file.save()
            send_file_messages_through_firebase(self.file, is_new=False)
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
