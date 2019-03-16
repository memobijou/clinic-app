from rest_framework import viewsets
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status, serializers
from filestorage.models import File, FileDirectory
from django.shortcuts import get_object_or_404
from abc import ABCMeta, abstractmethod
from decimal import Decimal


class FileSerializerBase(serializers.ModelSerializer):
    type = serializers.StringRelatedField()

    class Meta:
        model = File
        fields = ("file", "parent_directory", "type", "pk", "version")


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
        data = request.data
        version = self.request.POST.get("version")
        if version == "":
            self.file.version += Decimal(0.01)
        print(f"empty ? {type(self.request.POST.get('version'))}")
        file_serializer = FileUpdateSerializer(data=data, instance=self.file)

        if file_serializer.is_valid():
            print(f"hehe: {self.file.pk}")
            print(f"haha: {request.FILES}")
            version = request.POST.get("version")
            print(f"hey: {version}")
            if version:
                self.file.version = version
            self.file.file = request.FILES.get("file")
            self.file.save()
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


class FileDirectorySerializer(serializers.ModelSerializer):
    files = FileSerializer(many=True)

    class Meta:
        model = FileDirectory
        fields = ("name", "type", "files")

    def save(self, **kwargs):
        super().save(**kwargs)


# ViewSets define the view behavior.
class DirectoryViewSet(viewsets.ModelViewSet):
    queryset = FileDirectory.objects.all()
    serializer_class = FileDirectorySerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        self.queryset = super().get_queryset()
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
