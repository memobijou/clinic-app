from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.
from filestorage.forms import DirectoryForm
from filestorage.models import FileDirectory
from django.urls import reverse_lazy


class FileTreeView(LoginRequiredMixin, View):
    template_name = "filestorage/tree/tree.html"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tree = FileDirectory.objects.all()
        self.context = None
        self.directory_form = None

    def dispatch(self, request, *args, **kwargs):
        self.directory_form = self.get_directory_form()
        self.context = self.get_context()
        return super().dispatch(request, *args, **kwargs)

    def get_context(self):
        return {"tree": self.tree, "directory_form": self.directory_form}

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.context)

    def get_directory_form(self):
        if self.request.method == "POST":
            self.directory_form = DirectoryForm(data=self.request.POST)
        else:
            self.directory_form = DirectoryForm()
        return self.directory_form

    def post(self, request, *args, **kwargs):
        if self.directory_form.is_valid() is True:
            self.directory_form.save()
            return HttpResponseRedirect(reverse_lazy("filestorage:tree"))
        else:
            return render(request, self.template_name, self.context)
