from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from phonebook.forms import PhoneBookForm
from phonebook.models import PhoneBook
from django.shortcuts import get_object_or_404


class PhoneBookCreateView(LoginRequiredMixin, generic.CreateView):
    template_name = "phonebook/new.html"
    form_class = PhoneBookForm


class PhoneBookListView(LoginRequiredMixin, generic.ListView):
    queryset = PhoneBook.objects.all()


class PhoneBookUpdateView(LoginRequiredMixin, generic.UpdateView):
    form_class = PhoneBookForm
    template_name = "phonebook/edit.html"

    def get_object(self, queryset=None):
        return get_object_or_404(PhoneBook, pk=self.kwargs.get("pk"))
