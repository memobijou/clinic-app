from django.db.models import Q
from account.models import User
from taskmanagement.utils import send_push_notifications
from uniklinik.forms import BootstrapModelFormMixin
from taskmanagement.models import Task, UserTask
from account.models import Group
from django import forms
from django.db import transaction
from django.contrib.auth.models import User


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

    @transaction.atomic
    def save(self, commit=True):
        users = self.cleaned_data.pop("users")
        instance = super().save(commit=True)
        new_groups = self.cleaned_data.get("groups")

        for new_group in new_groups:
            instance.groups_list.add(new_group)

        all_users = User.objects.filter(Q(groups_list__in=new_groups) | Q(id__in=users)).distinct()
        UserTask.objects.bulk_create([UserTask(user=user, task=instance) for user in all_users])
        send_push_notifications(all_users, instance.name, instance.description, "task")
        return instance


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
        users = self.cleaned_data.pop("users")
        user_ids_before_save = list(self.instance.users.values_list("pk", flat=True))
        user_ids_after_save = list(users.values_list("pk", flat=True))

        instance = super().save(commit=True)
        UserTask.objects.filter(task=instance).exclude(user__in=users).delete()
        UserTask.objects.bulk_create([UserTask(user=user, task=instance) for user in
                                      users.exclude(usertasks__task=instance).distinct()])

        users_deleted = User.objects.filter(pk__in=user_ids_before_save).exclude(pk__in=user_ids_after_save)
        print(f"GELÖSCHT: {users_deleted}")

        new_users = User.objects.filter(pk__in=user_ids_after_save).exclude(pk__in=user_ids_before_save)
        print(f"NEUE NUTZER: {new_users}")

        send_push_notifications(users_deleted, f"AUFGEHOBEN: {instance.name}", instance.description,
                                "task")
        send_push_notifications(new_users, f"{instance.name}", instance.description, "task")
        return instance
