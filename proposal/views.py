from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from proposal.forms import TypeForm, ProposalForm
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from proposal.models import Type, Proposal
from django.http.response import HttpResponseRedirect


class TypeListView(LoginRequiredMixin, generic.CreateView):
    form_class = TypeForm
    template_name = "proposal/type/type_list.html"
    success_url = reverse_lazy("proposal:list-type")


class TypeUpdateView(LoginRequiredMixin, generic.UpdateView):
    form_class = TypeForm
    template_name = "proposal/type/edit/edit.html"

    def get_object(self, queryset=None):
        instance = get_object_or_404(Type, pk=self.kwargs.get("pk"))
        return instance

    def get_success_url(self):
        return reverse_lazy("proposal:edit-type", kwargs={"pk": self.object.pk})


class ProposalListView(LoginRequiredMixin, generic.CreateView):
    form_class = ProposalForm
    template_name = "proposal/list.html"
    success_url = reverse_lazy("proposal:list")


class ProposalUpdateView(LoginRequiredMixin, generic.UpdateView):
    form_class = ProposalForm
    template_name = "proposal/edit/edit.html"

    def get_object(self, queryset=None):
        instance = get_object_or_404(Proposal, pk=self.kwargs.get("pk"))
        return instance

    def get_success_url(self):
        return reverse_lazy("proposal:edit", kwargs={"pk": self.object.pk})


class ProposalDeleteView(LoginRequiredMixin, generic.DeleteView):
    def post(self, request, *args, **kwargs):
        items = request.POST.getlist("item")
        print(f"?????!!! {items}")
        Proposal.objects.filter(pk__in=items).delete()
        return HttpResponseRedirect(reverse_lazy("proposal:list"))
