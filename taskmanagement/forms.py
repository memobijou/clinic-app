from django.contrib.auth.models import User

from uniklinik.forms import BootstrapModelFormMixin
from taskmanagement.models import Task, UserTask
from account.models import Group
from django import forms
from django.db import transaction


class CreateTaskForm(BootstrapModelFormMixin):
    groups = forms.ModelMultipleChoiceField(queryset=Group.objects.all(), widget=forms.CheckboxSelectMultiple,
                                            label="Gruppen")
    users = forms.ModelMultipleChoiceField(queryset=User.objects.all(),
                                           widget=forms.CheckboxSelectMultiple,
                                           label="Benutzer", required=False)
    # User.objects.filter(usertasks__removed=False).distinct()

    class Meta:
        model = Task
        fields = ("name", "description", "start_datetime", "end_datetime", "groups", "users")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fields['description'].widget.attrs['rows'] = 3
        self.fields["start_datetime"].widget.attrs["class"] += " datetimepicker"
        self.fields["start_datetime"].widget.attrs["style"] = " width:50%;"
        self.fields["end_datetime"].widget.attrs["class"] += " datetimepicker"
        self.fields["end_datetime"].widget.attrs["style"] = " width:50%;"


class EditTaskForm(BootstrapModelFormMixin):
    users = forms.ModelMultipleChoiceField(queryset=User.objects.all(),
                                           widget=forms.CheckboxSelectMultiple,
                                           label="Benutzer", required=False)

    class Meta:
        model = Task
        fields = ("start_datetime", "end_datetime", "users",)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fields["start_datetime"].widget.attrs["class"] += " datetimepicker"
        self.fields["end_datetime"].widget.attrs["class"] += " datetimepicker"

    @transaction.atomic
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.save()
        users = self.cleaned_data.get("users")
        UserTask.objects.filter(task=instance).exclude(user__in=users).delete()
        UserTask.objects.bulk_create([UserTask(user=user, task=instance) for user in
                                      users.exclude(usertasks__task=instance).distinct()])
