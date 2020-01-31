from django.http import HttpResponseRedirect
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.
from subject_area.forms import SubjectAreaForm, CategoryForm
from subject_area.models import SubjectArea, Category
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.db.transaction import atomic


class SubjectAreaCreateView(LoginRequiredMixin, generic.CreateView):
    form_class = SubjectAreaForm
    template_name = "subject_area/new.html"


class SubjectAreaListView(LoginRequiredMixin, generic.ListView):
    model = SubjectArea


class SubjectAreaUpdateView(LoginRequiredMixin, generic.UpdateView):
    form_class = SubjectAreaForm
    template_name = "subject_area/edit.html"

    def get_object(self, queryset=None):
        return get_object_or_404(SubjectArea, pk=self.kwargs.get("pk"))


class CreateCategoryView(LoginRequiredMixin, generic.CreateView):
    form_class = CategoryForm
    template_name = "subject_area/category/new/new.html"
    subject_area_object = None

    def dispatch(self, request, *args, **kwargs):
        self.subject_area_object = get_object_or_404(SubjectArea, pk=self.kwargs.get("pk"))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["subject_area_object"] = self.subject_area_object
        return context

    @atomic
    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.subject_area = self.subject_area_object
        print(self.subject_area_object.pk)
        instance.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy("subject_area:new-category", kwargs={"pk": self.subject_area_object.pk})


class UpdateCategoryView(LoginRequiredMixin, generic.UpdateView):
    form_class = CategoryForm
    template_name = "subject_area/category/edit/edit.html"
    subject_area_object = None
    instance = None

    def dispatch(self, request, *args, **kwargs):
        self.instance = get_object_or_404(Category, pk=self.kwargs.get("category_pk"))
        self.subject_area_object = self.instance.subject_area
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["subject_area_object"] = self.subject_area_object
        return context

    def get_object(self, queryset=None):
        return get_object_or_404(Category, pk=self.kwargs.get("category_pk"))

    def get_success_url(self):
        return reverse_lazy("subject_area:edit-category", kwargs={
            "pk": self.subject_area_object.pk, "category_pk": self.instance.pk})


class CategoryDeleteView(LoginRequiredMixin, generic.DeleteView):
    instance = None

    def dispatch(self, request, *args, **kwargs):
        self.instance = get_object_or_404(Category, pk=self.kwargs.get("category_pk"))
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return self.instance

    def get_success_url(self):
        return reverse_lazy("subject_area:new-category", kwargs={"pk": self.instance.subject_area.pk})
