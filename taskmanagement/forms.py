from django.contrib.auth.models import User

from uniklinik.forms import BootstrapModelForm
from taskmanagement.models import Task
from account.models import Group
from django import forms

class GroupTaskForm(BootstrapModelForm):
    groups = forms.ModelMultipleChoiceField(queryset=Group.objects.all(),
                                            widget=forms.CheckboxSelectMultiple
                                            )
    class Meta:
        model = Task
        fields = ("name", "groups", )


class UserTaskForm(BootstrapModelForm):
    class Meta:
        model = Task
        fields = ("users", )
        widgets = {"users": forms.CheckboxSelectMultiple}

    def __init__(self, group=None, **kwargs):
        super().__init__(**kwargs)
        queryset = self.fields["users"].queryset
        self.fields["users"].queryset = queryset.filter(groups_list__in=[group]).distinct()
