from decimal import Decimal
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
from django.http import HttpResponse, HttpResponseNotFound
from filestorage.models import FileDirectory, File
from abc import ABCMeta, abstractmethod
from django.shortcuts import get_object_or_404
import os
import boto3
from django.conf import settings


class UserDirectoryViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = FileDirectory.objects.all()
    serializer_class = FileDirectorySerializer
    pagination_class = PageNumberPagination

    def get_serializer_context(self):
        return {"request": self.request, "user_id": self.kwargs.get("user_id"), "pk": self.kwargs.get("pk")}

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

        # if directory_id:
        #     FileUserHistory.objects.filter(user_id=user_id, file__parent_directory_id=directory_id).distinct().update(
        #      unread_notifications=0)

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

    def get_serializer_context(self):
        return {"request": self.request, "pk": self.kwargs.get("pk")}

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

    def get_serializer_context(self):
        return {"request": self.request, "pk": self.kwargs.get("pk")}

    def post(self, request, *args, **kwargs):
        self.directory = get_object_or_404(FileDirectory, pk=self.kwargs.get("directory_pk"))
        file_serializer = FileSerializer(data=request.data, context=self.get_serializer_context())

        if file_serializer.is_valid():
            print(f"hehe: {self.directory.pk}")
            print(f"haha: {request.FILES}")
            file_serializer.save(parent_directory=self.directory, file=request.FILES.get("file"))
            return Response(file_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FileUploadUpdateView(IFileUploadView):
    file = None

    def get_serializer_context(self):
        return {"request": self.request, "pk": self.kwargs.get("pk")}

    def post(self, request, *args, **kwargs):
        self.file = get_object_or_404(File, pk=self.kwargs.get("file_pk"))
        origin_file = self.file.file
        data = request.data
        version = self.request.POST.get("version")
        name = self.request.POST.get("name")

        if not version:
            self.file.version += Decimal(0.01)

        file_serializer = FileUpdateSerializer(data=data, instance=self.file, context=self.get_serializer_context())

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


class ServeFileView(APIView):
    def get(self, request, pk, user_id=None, format=None):
        file = File.objects.get(pk=pk)

        if pk and user_id:
            file.fileuserhistory_set.filter(user_id=user_id).update(unread_notifications=0)

        if hasattr(settings, "AWS_ACCESS_KEY_ID"):
            s3 = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                              aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)

            key = os.path.join(file.file.storage.location, file.file.name)
            print(f"?????: {key}")
            response = s3.get_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=key)
            f = response['Body']
            response = HttpResponse(f.read(), content_type='application/force-download')
            filename = key.split("/")[len(key.split("/")) - 1]
            response['Content-Disposition'] = f'attachment; filename=\"{filename}\"'
            return response
        else:
            import mimetypes
            mimetypes.init()

            try:
                file_path = file.file.path
                print(f"wer ist das: {file_path}")
                print(f"wer ist das: {file.file.name}")
                fsock = open(file_path, "rb")
                # file = fsock.read()
                # fsock = open(file_path,"r").read()
                file_name = os.path.basename(file_path)
                file_size = os.path.getsize(file_path)
                mime_type_guess = mimetypes.guess_type(file_name)
                response = None
                if mime_type_guess is not None:
                    response = HttpResponse(fsock)
                    response['Content-Disposition'] = 'attachment; filename=' + file_name
            except IOError:
                response = HttpResponseNotFound()
            return response
