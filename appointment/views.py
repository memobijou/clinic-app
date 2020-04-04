from django.contrib.auth.models import User
from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views import View
# Create your views here.
from django import forms
from appointment.models import Appointment
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from pyfcm import FCMNotification
from pyfcm.errors import AuthenticationError, FCMServerError, InvalidDataError, InternalPackageError
import os
from uniklinik.forms import BootstrapModelFormMixin
from account.models import Profile
from uniklinik.utils import send_push_notifications


class ConferenceFormMixin(BootstrapModelFormMixin):
    class Meta:
        model = Appointment
        fields = ["start_date", "end_date", "topic", "description", "place", "groups"]
        widgets = {
            'groups': forms.CheckboxSelectMultiple,
        }

    def clean(self):
        return super().clean()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fields["start_date"].widget.attrs["class"] = "datetimepicker form-control"
        self.fields["end_date"].widget.attrs["class"] = "datetimepicker form-control"
        self.fields["description"].widget.attrs["rows"] = "5"


class AppointmentView(LoginRequiredMixin, View):
    template_name = "appointment/appointment.html"

    def __init__(self):
        super().__init__()
        self.edit_conference_form = None
        self.conference_form = None

    def dispatch(self, request, *args, **kwargs):
        self.edit_conference_form = self.get_edit_conference_form()
        self.conference_form = self.get_conference_form()
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context())

    def get_conference_form(self):
        if self.request.method == "POST":
            self.conference_form = ConferenceFormMixin(data=self.request.POST)
        else:
            self.conference_form = ConferenceFormMixin()
        return self.conference_form

    def get_edit_conference_form(self):
        if self.request.method == "POST":
            self.edit_conference_form = ConferenceFormMixin(prefix="edit", data=self.request.POST)
        else:
            self.edit_conference_form = ConferenceFormMixin(prefix="edit")
        return self.edit_conference_form

    def get_context(self):
        return {"conference_form": self.conference_form, "edit_conference_form": self.edit_conference_form}


def get_users_from_groups(groups):
    users = User.objects.filter(groups_list__in=groups).distinct()
    return users


class ConferenceView(LoginRequiredMixin, View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.conference_form = None

    def dispatch(self, request, *args, **kwargs):
        self.conference_form = self.get_conference_form()
        return super().dispatch(request, *args, **kwargs)

    def get_conference_form(self):
        if self.request.method == "POST":
            self.conference_form = ConferenceFormMixin(data=self.request.POST)
        else:
            self.conference_form = ConferenceFormMixin()
        return self.conference_form

    def post(self, request, *args, **kwargs):
        if self.conference_form.is_valid() is True:
            instance = self.conference_form.save()
            instance.promoter = request.user
            instance.save()
            users = get_users_from_groups(instance.groups.all())

            def update_badge_method(push_user_ids):
                Profile.objects.filter(user_id__in=push_user_ids).update(appointment_badges=F("appointment_badges") + 1)

            send_push_notifications(users, instance.topic, instance.description, "appointment", update_badge_method)
            return HttpResponseRedirect(reverse_lazy("appointment:planning"))
        else:
            return render(request, "appointment/appointment.html", self.get_context())

    def get_context(self):
        return {"conference_form": self.conference_form}


class ConferenceUpdateView(LoginRequiredMixin, View):
    def __init__(self):
        super().__init__()
        self.edit_conference_form = None
        self.object = None
        self.conference_form = None

    def dispatch(self, request, *args, **kwargs):
        self.object = get_object_or_404(Appointment, pk=self.kwargs.get("pk"))
        self.edit_conference_form = self.get_edit_conference_form()
        self.conference_form = self.get_conference_form()
        return super().dispatch(request, *args, **kwargs)

    def get_edit_conference_form(self):
        if self.request.method == "POST":
            self.edit_conference_form = ConferenceFormMixin(prefix="edit", data=self.request.POST, instance=self.object)
        else:
            self.edit_conference_form = ConferenceFormMixin(prefix="edit", instance=self.object)
        return self.edit_conference_form

    def post(self, request, *args, **kwargs):
        if self.edit_conference_form.is_valid() is True:
            self.edit_conference_form.save()
            users = get_users_from_groups(self.object.groups.all())

            def update_badge_method(push_user_ids):
                Profile.objects.filter(user_id__in=push_user_ids).update(appointment_badges=F("appointment_badges") + 1)

            send_push_notifications(users, self.object.topic, self.object.description, "appointment",
                                    update_badge_method)
            return HttpResponseRedirect(reverse_lazy("appointment:planning"))
        else:
            return render(request, "appointment/appointment.html", {"edit_conference_form": self.edit_conference_form,
                                                                    "conference_form": self.conference_form})

    def get_conference_form(self):
        if self.request.method == "POST":
            self.conference_form = ConferenceFormMixin(initial=self.request.POST)
        else:
            self.conference_form = ConferenceFormMixin()
        return self.conference_form


class AppointmentDeleteView(View):
    def post(self, request, *args, **kwargs):
        items = request.GET.getlist("item")
        Appointment.objects.filter(pk__in=items).delete()
        return HttpResponseRedirect(reverse_lazy("appointment:planning"))
