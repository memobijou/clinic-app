from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.
from filestorage.forms import FileDirectoryForm, DownloadForm
from filestorage.models import FileDirectory, File
from django.urls import reverse_lazy
from abc import ABCMeta, abstractmethod
from django.shortcuts import get_object_or_404


class FileDirectoryBaseView(LoginRequiredMixin, View, metaclass=ABCMeta):
    @property
    @abstractmethod
    def template_name(self):
        pass

    @property
    @abstractmethod
    def success_url(self):
        pass

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.file_directories = FileDirectory.objects.filter(type="filestorage")
        self.context = None
        self.directory_form = None

    def dispatch(self, request, *args, **kwargs):
        self.directory_form = self.get_directory_form()
        self.context = self.get_context()
        return super().dispatch(request, *args, **kwargs)

    def get_context(self):
        return {"file_directories": self.file_directories, "directory_form": self.directory_form}

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.context)

    @abstractmethod
    def get_directory_form(self):
        pass

    def post(self, request, *args, **kwargs):
        if self.directory_form.is_valid() is True:
            self.directory_form.save()
            return HttpResponseRedirect(self.success_url)
        else:
            return render(request, self.template_name, self.context)


class FileDirectoryView(FileDirectoryBaseView):
    template_name = "filestorage/filestorage.html"
    success_url = reverse_lazy("filestorage:tree")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.file_directories = FileDirectory.objects.filter(type="filestorage")

    def get_directory_form(self):
        if self.request.method == "POST":
            self.directory_form = FileDirectoryForm(data=self.request.POST)
        else:
            self.directory_form = FileDirectoryForm()
        return self.directory_form


class DownloadView(FileDirectoryBaseView):
    template_name = "filestorage/download/download.html"
    success_url = reverse_lazy("filestorage:download")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.file_directories = FileDirectory.objects.filter(type="download")

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
    @property
    @abstractmethod
    def success_url(self):
        pass

    def post(self, request, *args, **kwargs):
        instance = get_object_or_404(FileDirectory, pk=self.kwargs.get("pk"))
        if instance.announcement in [False, None]:
            instance.announcement = True
        else:
            instance.announcement = None
        instance.save()
        return HttpResponseRedirect(self.success_url)


class FilestorageSubscribeAnnouncement(BaseSubscribeAnnouncement):
    success_url = reverse_lazy("filestorage:tree")


class DownloadSubscribeAnnouncement(BaseSubscribeAnnouncement):
    success_url = reverse_lazy("filestorage:donwload")
