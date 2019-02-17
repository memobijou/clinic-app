from django.http import HttpResponseRedirect
from django.views import generic
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from account.models import Group
from django import forms
from django.urls import reverse_lazy
from uniklinik.forms import BootstrapModelForm
from django.shortcuts import render


class GroupListView(LoginRequiredMixin, generic.ListView):
    template_name = "group/group_list.html"
    paginate_by = 15
    queryset = Group.objects.all()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = GroupForm
        return context


class GroupForm(BootstrapModelForm):
    class Meta:
        model = Group
        fields = ("name", )

    def clean_name(self):
        name = self.cleaned_data.get("name")
        if Group.objects.filter(name__iexact=name).count() > 0:
            self.add_error("name", "Eintrag bereits vorhanden")
        return name


class GroupUsersForm(BootstrapModelForm):
    class Meta:
        model = Group
        fields = ("name", "users", )
        widgets = {
            'users': forms.CheckboxSelectMultiple,
        }

    def clean_name(self):
        name = self.cleaned_data.get("name")
        print(f"heyyyyyy {name} - {self.instance.name}")
        if name != self.instance.name:
            if Group.objects.filter(name__iexact=name).count() > 0:
                self.add_error("name", "Eintrag bereits vorhanden")
        return name


class GroupCreateView(LoginRequiredMixin, generic.CreateView):
    form_class = GroupForm
    success_url = reverse_lazy("account:group_list")
    template_name = "group/group_list.html"


class GroupUpdateView(LoginRequiredMixin, generic.UpdateView):
    form_class = GroupUsersForm
    success_url = reverse_lazy("account:group_list")
    template_name = "group/forms/form.html"

    def get_object(self, queryset=None):
        return Group.objects.get(pk=self.kwargs.get("pk"))
