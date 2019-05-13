from django.db import transaction
from django.db.models import Case, When, Value, IntegerField, Count
from django.http import HttpResponseRedirect
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from account.models import Group
from django import forms
from django.urls import reverse_lazy
from uniklinik.forms import BootstrapModelFormMixin
from django.contrib.auth.models import User


class GroupListView(LoginRequiredMixin, generic.ListView):
    template_name = "group/group_list.html"
    paginate_by = 15
    queryset = Group.objects.all()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = GroupFormMixin
        return context


class GroupFormMixin(BootstrapModelFormMixin):
    class Meta:
        model = Group
        fields = ("name", )

    def clean_name(self):
        name = self.cleaned_data.get("name")
        if Group.objects.filter(name__iexact=name).count() > 0:
            self.add_error("name", "Eintrag bereits vorhanden")
        return name


class GroupUsersFormMixin(BootstrapModelFormMixin):
    class Meta:
        model = Group
        fields = ("name", "users",)
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
    form_class = GroupFormMixin
    success_url = reverse_lazy("account:group_list")
    template_name = "group/group_list.html"


class GroupUpdateView(LoginRequiredMixin, generic.UpdateView):
    form_class = GroupUsersFormMixin
    success_url = reverse_lazy("account:group_list")
    template_name = "group/forms/form.html"

    def get_object(self, queryset=None):
        return Group.objects.get(pk=self.kwargs.get("pk"))


class GroupDeletionView(generic.View):
    @transaction.atomic
    def dispatch(self, request, *args, **kwargs):
        if request.method == "POST":
            items = request.POST.getlist("item")
            groups = Group.objects.filter(id__in=items)
            print(f"he: {groups}")
            groups.delete()
            return HttpResponseRedirect(reverse_lazy("account:group_list"))
