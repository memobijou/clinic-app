from django.db.models import Count, Q, F
from django.http import HttpResponseRedirect, HttpResponse
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
        directory = get_object_or_404(FileDirectory, pk=self.kwargs.get("directory_pk"))
        directory_ids = request.POST.getlist("directory")
        parent_id = directory.parent_id
        print(f"directory.parent_id {parent_id}")
        print(f"heyyyyy::: {directory_ids}")

        file_directories = FileDirectory.objects.filter(pk__in=directory_ids).annotate(
            count_files=Count("files")).annotate(count_child_directories=Count("child_directories")).filter(
            count_files=0, count_child_directories=0)

        full_directories = FileDirectory.objects.filter(pk__in=directory_ids).annotate(
            count_files=Count("files")).annotate(count_child_directories=Count("child_directories")).filter(
            Q(Q(count_files__gt=0) | Q(count_child_directories__gt=0)))

        full_directories_count = full_directories.count()

        for d in full_directories:
            print(f"d:: {d.count_files} {d.count_child_directories}")

        print(f"full_directories_count:: {full_directories_count}")

        if full_directories_count == 0:
            files = File.objects.filter(parent_directory=directory, pk__in=items)
            for file in files:
                file.file.delete()
            files.delete()
            file_directories.delete()

        try:
            directory.refresh_from_db()
            print(f"darf nicht !!!")
            context = {
                "url": str(reverse_lazy("filestorage:child_tree", kwargs={"parent_directory_pk": directory.pk}))
            }
            response = HttpResponse(json.dumps(context), content_type='application/json')
            response.status_code = 200
            return response
        except FileDirectory.DoesNotExist as e:
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
        finally:
            if full_directories_count > 0:
                context = {
                    "error": "Es können nur leere Ordner gelöscht werden. "
                }
                response = HttpResponse(json.dumps(context), content_type='application/json')
                response.status_code = 400
                return response
