from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, F
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound
from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.
from filestorage.forms import FileDirectoryForm, DownloadForm
from filestorage.models import FileDirectory, File
from django.urls import reverse_lazy
from abc import ABCMeta, abstractmethod
from django.shortcuts import get_object_or_404
import json
import os
import boto3
from django.conf import settings
from filestorage.models import filestorage_upload_to_path


class FileDirectoryBaseView(LoginRequiredMixin, View, metaclass=ABCMeta):
    @property
    @abstractmethod
    def template_name(self):
        pass

    @abstractmethod
    def get_success_url(self):
        pass

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.file_directories = None
        self.context = None
        self.directory_form = None
        self.parent_directory = None

    def dispatch(self, request, *args, **kwargs):
        parent_directory_pk = self.kwargs.get("parent_directory_pk")

        if parent_directory_pk is not None:
            self.file_directories = FileDirectory.objects.filter(parent__pk=parent_directory_pk)
            self.parent_directory = get_object_or_404(FileDirectory, pk=parent_directory_pk)
        else:
            self.file_directories = FileDirectory.objects.filter(parent__isnull=True)

        self.directory_form = self.get_directory_form()
        self.context = self.get_context()

        return super().dispatch(request, *args, **kwargs)

    def get_context(self):
        return {"file_directories": self.file_directories, "directory_form": self.directory_form,
                "parent_directory": self.parent_directory}

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.context)

    @abstractmethod
    def get_directory_form(self):
        pass

    def post(self, request, *args, **kwargs):
        if self.directory_form.is_valid() is True:
            self.directory_form.save()
            return HttpResponseRedirect(self.get_success_url())
        else:
            return render(request, self.template_name, self.context)


class FileDirectoryView(FileDirectoryBaseView):
    template_name = "filestorage/filestorage.html"

    def get_success_url(self):
        parent_directory_pk = self.kwargs.get("parent_directory_pk")

        if parent_directory_pk:
            return reverse_lazy("filestorage:child_tree", kwargs={"parent_directory_pk": parent_directory_pk})
        else:
            return reverse_lazy("filestorage:tree")

    def dispatch(self, request, *args, **kwargs):
        pre_dispatch = super().dispatch(request, *args, **kwargs)
        self.file_directories = self.file_directories.filter(type="filestorage")
        return pre_dispatch

    def get_directory_form(self):
        if self.request.method == "POST":
            self.directory_form = FileDirectoryForm(data=self.request.POST)
            if self.parent_directory is not None:
                self.directory_form.instance.parent = self.parent_directory
        else:
            self.directory_form = FileDirectoryForm()
        return self.directory_form


class DownloadView(FileDirectoryBaseView):
    template_name = "filestorage/download/download.html"
    success_url = reverse_lazy("filestorage:download")

    def dispatch(self, request, *args, **kwargs):
        pre_dispatch = super().dispatch(request, *args, **kwargs)
        self.file_directories = self.file_directories.filter(type="download")
        return pre_dispatch

    def get_directory_form(self):
        if self.request.method == "POST":
            self.directory_form = DownloadForm(data=self.request.POST)
        else:
            self.directory_form = DownloadForm()
        return self.directory_form


class FileView(LoginRequiredMixin, View):
    template_name = "filestorage/edit/edit.html"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.file = None

    def get(self, request, *args, **kwargs):
        self.file = File.objects.get(pk=self.kwargs.get("pk"))
        return render(request, self.template_name, {"file": self.file})


class BaseSubscribeAnnouncement(LoginRequiredMixin, View, metaclass=ABCMeta):
    @abstractmethod
    def get_success_url(self):
        pass

    def post(self, request, *args, **kwargs):
        instance = get_object_or_404(FileDirectory, pk=self.kwargs.get("pk"))
        if instance.announcement in [False, None]:
            instance.announcement = True
        else:
            instance.announcement = None
        instance.save()
        return HttpResponseRedirect(self.get_success_url())


class FilestorageSubscribeAnnouncement(BaseSubscribeAnnouncement):
    def get_success_url(self):
        redirect_directory_pk = self.kwargs.get("redirect_directory_pk")
        print(f"yaaaa: {redirect_directory_pk}")
        if redirect_directory_pk is None:
            return reverse_lazy("filestorage:tree")
        else:
            return reverse_lazy("filestorage:child_tree", kwargs={"parent_directory_pk": redirect_directory_pk})


class DownloadSubscribeAnnouncement(BaseSubscribeAnnouncement):
    def get_success_url(self):
        return reverse_lazy("filestorage:donwload")


class DeleteFileView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        items = request.POST.getlist("item")
        if self.kwargs.get("directory_pk"):
            directory = get_object_or_404(FileDirectory, pk=self.kwargs.get("directory_pk"))
        else:
            directory = None

        directory_ids = request.POST.getlist("directory")

        file_directories = FileDirectory.objects.filter(pk__in=directory_ids).annotate(
            count_files=Count("files")).annotate(count_child_directories=Count("child_directories")).filter(
            count_files=0, count_child_directories=0)

        full_directories = FileDirectory.objects.filter(pk__in=directory_ids).annotate(
            count_files=Count("files")).annotate(count_child_directories=Count("child_directories")).filter(
            Q(Q(count_files__gt=0) | Q(count_child_directories__gt=0)))

        full_directories_count = full_directories.count()

        parent_id = None
        if directory:
            parent_id = directory.parent_id

        self.delete_files_and_directories(full_directories_count, directory, items, file_directories)

        return self.return_http_response(directory, parent_id, full_directories_count)

    @staticmethod
    def delete_files_and_directories(full_directories_count, directory, items, file_directories):
        if full_directories_count == 0:
            if directory:
                files = File.objects.filter(parent_directory=directory, pk__in=items)
            else:
                files = File.objects.filter(parent_directory__isnull=True, pk__in=items)
            for file in files:
                file.file.delete()
            files.delete()
            file_directories.delete()

    def return_http_response(self, directory, parent_id, full_directories_count):
        if not directory:
            if full_directories_count > 0:
                return self.return_http_error_response()
            else:
                return self.return_success_response(parent_id)

        try:
            directory.refresh_from_db()
            return self.return_success_response(directory.id)
        except FileDirectory.DoesNotExist as e:
            return self.return_success_response(parent_id)
        finally:
            if full_directories_count > 0:
                return self.return_http_error_response()

    @staticmethod
    def return_http_error_response():
            context = {
                "error": "Es können nur leere Ordner gelöscht werden. "
            }
            response = HttpResponse(json.dumps(context), content_type='application/json')
            response.status_code = 400
            return response

    @staticmethod
    def return_success_response(parent_id):
        if not parent_id:
            context = {
                "url": str(reverse_lazy("filestorage:tree"))
            }
        else:
            context = {
                "url": str(reverse_lazy("filestorage:child_tree", kwargs={"parent_directory_pk": parent_id}))
            }
        response = HttpResponse(json.dumps(context), content_type='application/json')
        response.status_code = 200
        return response


@login_required
def serve_upload_files(request, pk):
    file = File.objects.get(pk=pk)
    if hasattr(settings, "AWS_ACCESS_KEY_ID"):
        s3 = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)

        key = file.file.path
        print(f"?????: {key}")
        response = s3.get_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=key)
        f = response['Body']
        response = HttpResponse(f.read(), content_type='application/force-download')
        filename = key.split("/")[len(key.split("/"))-1]
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
