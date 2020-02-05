from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from phonebook.forms import PhoneBookForm, CategoryForm
from phonebook.models import PhoneBook, Category
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy


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

    def get_success_url(self):
        return reverse_lazy("phonebook:edit", kwargs={"pk": self.kwargs.get("pk")})


class CategoryCreateView(LoginRequiredMixin, generic.CreateView):
    template_name = "phonebook/category_list.html"
    form_class = CategoryForm

    def get_success_url(self):
        return reverse_lazy("phonebook:category-list")


class CategoryUpdateView(LoginRequiredMixin, generic.UpdateView):
    form_class = CategoryForm
    template_name = "phonebook/category/edit.html"

    def get_object(self, queryset=None):
        return get_object_or_404(Category, pk=self.kwargs.get("pk"))

    def get_success_url(self):
        return reverse_lazy("phonebook:category-edit", kwargs={"pk": self.kwargs.get("pk")})
