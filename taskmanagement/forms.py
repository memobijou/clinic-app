from django.contrib.auth.models import User

from uniklinik.forms import BootstrapModelFormMixin
from taskmanagement.models import Task
from account.models import Group
from django import forms


class GroupTaskFormMixin(BootstrapModelFormMixin):
    groups = forms.ModelMultipleChoiceField(queryset=Group.objects.all(),
                                            widget=forms.CheckboxSelectMultiple, label="Gruppen"
                                            )

    class Meta:
        model = Task
        fields = ("name", "description", "groups", )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fields['description'].widget.attrs['rows'] = 3


class UserTaskFormMixin(BootstrapModelFormMixin):
    class Meta:
        model = Task
        fields = ("users", )
        widgets = {"users": forms.CheckboxSelectMultiple}

    def __init__(self, group=None, **kwargs):
        super().__init__(**kwargs)
        queryset = self.fields["users"].queryset
        self.fields["users"].queryset = queryset.filter(groups_list__in=[group]).distinct()
