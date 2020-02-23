from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from proposal.forms import TypeForm
from django.urls import reverse_lazy


class TypeListView(LoginRequiredMixin, generic.CreateView):
    form_class = TypeForm
    template_name = "proposal/type/type_list.html"
    success_url = reverse_lazy("proposal:list-type")
