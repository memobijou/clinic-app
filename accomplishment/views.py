from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Q, Case, When, F
from django.shortcuts import render
from django.views import generic
# Create your views here.
from accomplishment.forms import AccomplishmentFormMixin
from accomplishment.models import Accomplishment
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from accomplishment.utils import get_accomplishment_scores


class AccomplishmentListView(LoginRequiredMixin, generic.CreateView):
    form_class = AccomplishmentFormMixin
    template_name = "accomplishment/accomplishment_list.html"
    success_url = reverse_lazy("accomplishment:list")


class AccomplishmentUpdateView(LoginRequiredMixin, generic.UpdateView):
    form_class = AccomplishmentFormMixin
    template_name = "accomplishment/edit/edit.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = dict(**context, **get_accomplishment_scores(self.get_object()))
        return context

    def get_object(self, queryset=Accomplishment.objects.prefetch_related("users")):
        # print(queryset.first()._prefetched_objects_cache)
        return get_object_or_404(queryset, pk=self.kwargs.get("pk"))

    def get_success_url(self):
        return reverse_lazy("accomplishment:edit", kwargs={"pk": self.object.pk})
