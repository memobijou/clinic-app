from django.db.models import Case, When, Value, IntegerField, Count
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
    choices = ((None, "--------"), ("discipline", "Fachrichtung"))
    type = forms.ChoiceField(choices=choices, label="Art", required=False)

    class Meta:
        model = Group
        fields = ("name", "users", "type", )
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

    def clean(self):
        cleaned_data = super().clean()
        print(f"FACHRICHTUNG: {cleaned_data.get('users')}")
        users = cleaned_data.get("users")
        users_with_discipline = users.annotate(
            discipline_amount=Count(Case(When(groups_list__type__iexact="discipline", then=Value(1)),
                                         output_field=IntegerField()))).filter(discipline_amount__gte=1)

        if self.instance:
            users_with_discipline = users_with_discipline.exclude(groups_list__pk=self.instance.pk)

        users_with_discipline = users_with_discipline.distinct()

        if users_with_discipline.count() > 0:
            error_msg = "Folgende Nutzer sind bereits einer Fachrichtung zugewiesen: "
            for user in users_with_discipline:
                error_msg += f"{user}, "
            error_msg = error_msg[:-1]
            error_msg = error_msg[:-1]
            self.add_error(None, error_msg)
        return cleaned_data


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
