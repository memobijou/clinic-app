from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status, serializers
from django.urls import reverse
from rest_framework.viewsets import GenericViewSet
from filestorage.utils import send_push_notifications
from filestorage.models import File, FileDirectory
from django.shortcuts import get_object_or_404
from abc import ABCMeta, abstractmethod
from decimal import Decimal
from rest_framework import mixins
from django.contrib.auth.models import User


def send_file_messages_through_firebase(file, is_new=True):
    if file.parent_directory.announcement is True:
        if is_new is True:
            title = f"Neue Datei in {file.parent_directory.name}"
            message = f'"{file.file.name}" Version {file.version_with_point}'
        else:
            title = f"Update vorhanden in {file.parent_directory.name}"
            message = f"{file.file.name} jetzt auf Version {file.version_with_point}"
        send_push_notifications(User.objects.all(), title, message, "filestorage")
        print(message)
        print(title)


class FileSerializerBase(serializers.ModelSerializer):
    type = serializers.StringRelatedField()
    filename = serializers.SerializerMethodField()

    def get_filename(self, instance):
        return instance.file.name

    class Meta:
        model = File
        fields = ("file", "parent_directory", "type", "pk", "version", "filename")

    def save(self, **kwargs):
        instance = super().save(**kwargs)
        send_file_messages_through_firebase(instance)
        return instance


class FileSerializer(FileSerializerBase):
    pass


class FileUpdateSerializer(FileSerializerBase):
    def validate_version(self, value):
        print(f"version 1: {type(value)}")
        print(f"version 2: {value}")
        if type(value) not in [float, int, Decimal]:
            raise serializers.ValidationError(f"Sie müssen eine Zahl eingeben")
        if value <= self.instance.version:
            raise serializers.ValidationError(f"Version muss größer als {self.instance.version} sein")
        return value


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


# ViewSets define the view behavior.
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


class FileDirectorySerializer(serializers.ModelSerializer):
    files = FileSerializer(many=True)
    child_directories = serializers.SerializerMethodField()

    def get_child_directories(self, value):
        child_directories_queryset = value.child_directories.values("name", "pk")
        for child_directory in child_directories_queryset:
            request = self.context.get("request")
            user_id = self.context.get("user_id")
            if user_id:
                url = reverse("api_filestorage:directories-detail", kwargs={"pk": child_directory.get("pk"),
                                                                            "user_id": user_id})
            else:
                url = reverse("filestorage:directories-detail", kwargs={"pk": child_directory.get("pk")})
            if request:
                child_directory["link"] = request.build_absolute_uri(url)
            else:
                child_directory["link"] = url
        result = [child_directories_queryset]
        return result

    parent = serializers.SerializerMethodField()

    def get_parent(self, value):
        if value.parent:
            request = self.context.get("request")
            url = reverse("api_filestorage:directories-detail", kwargs={"pk": value.parent.pk})
            parent_dict = {"name": value.name, "pk": value.id}
            if request:
                parent_dict["link"] = request.build_absolute_uri(url)
            else:
                parent_dict["link"] = url
            result = parent_dict
            return result

    class Meta:
        model = FileDirectory
        fields = ("pk", "name", "type", "files", "child_directories", "parent", )

    def save(self, **kwargs):
        super().save(**kwargs)


# ViewSets define the view behavior.
class DirectoryViewSet(viewsets.ModelViewSet):
    queryset = FileDirectory.objects.all()
    serializer_class = FileDirectorySerializer
    pagination_class = PageNumberPagination

    def get_serializer_context(self):
        return {"request": self.request}

    def get_queryset(self):
        self.queryset = super().get_queryset()
        if not self.kwargs.get("pk"):
            self.queryset = self.queryset.filter(parent__isnull=True)
        self.filter_by_name()
        self.filter_by_name_exact()
        return self.queryset

    def filter_by_name(self):
        name = self.request.GET.get("name")
        if name is not None:
            self.queryset = self.queryset.filter(name__icontains=name)

    def filter_by_name_exact(self):
        name = self.request.GET.get("name_exact")
        if name is not None:
            self.queryset = self.queryset.filter(name__iexact=name)


# ViewSets define the view behavior.
class UserDirectoryViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = FileDirectory.objects.all()
    serializer_class = FileDirectorySerializer
    pagination_class = PageNumberPagination

    def get_serializer_context(self):
        return {"request": self.request, "user_id": self.kwargs.get("user_id")}

    def get_queryset(self):
        self.queryset = super().get_queryset()

        if not self.kwargs.get("pk"):
            self.queryset = self.queryset.filter(parent__isnull=True)
        self.filter_by_name()
        self.filter_by_name_exact()

        if self.kwargs.get("user_id"):
            user = get_object_or_404(User, pk=self.kwargs.get("user_id"))
            user.profile.filestorage_badges = 0
            user.profile.save()
        return self.queryset

    def filter_by_name(self):
        name = self.request.GET.get("name")
        if name is not None:
            self.queryset = self.queryset.filter(name__icontains=name)

    def filter_by_name_exact(self):
        name = self.request.GET.get("name_exact")
        if name is not None:
            self.queryset = self.queryset.filter(name__iexact=name)
