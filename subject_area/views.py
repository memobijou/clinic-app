from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.
from subject_area.forms import SubjectAreaForm
from subject_area.models import SubjectArea
from django.shortcuts import get_object_or_404


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
