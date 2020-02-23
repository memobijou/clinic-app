from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django.urls import reverse_lazy
# Create your views here.
from poll.forms import PollForm, PollUpdateForm, OptionForm
from poll.models import Poll, Option


class PollListView(LoginRequiredMixin, generic.CreateView):
    form_class = PollForm
    template_name = "poll/poll_list.html"
    success_url = reverse_lazy("poll:list")


class PollUpdateView(LoginRequiredMixin, generic.UpdateView):
    form_class = PollUpdateForm
    template_name = "poll/edit/edit.html"

    def get_object(self, queryset=None):
        instance = get_object_or_404(Poll, pk=self.kwargs.get("pk"))
        return instance

    def get_success_url(self):
        return reverse_lazy("poll:edit", kwargs={"pk": self.object.pk})


class OptionUpdateView(LoginRequiredMixin, generic.UpdateView):
    form_class = OptionForm
    template_name = "poll/option/edit.html"

    def get_object(self, queryset=None):
        instance = get_object_or_404(Option, pk=self.kwargs.get("option_pk"))
        return instance

    def get_success_url(self):
        return reverse_lazy("poll:edit-option", kwargs={"pk": self.object.poll_id, "option_pk": self.object.pk})


class OptionDeleteView(LoginRequiredMixin, generic.DeleteView):
    template_name = "poll/option/edit.html"

    def get_object(self, queryset=None):
        instance = get_object_or_404(Option, pk=self.kwargs.get("option_pk"))
        return instance

    def get_success_url(self):
        return reverse_lazy("poll:edit", kwargs={"pk": self.kwargs.get("pk")})
