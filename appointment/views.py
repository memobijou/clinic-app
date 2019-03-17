from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views import View
# Create your views here.
from django import forms
from appointment.models import Appointment
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from pyfcm import FCMNotification
import os
from uniklinik.forms import BootstrapModelForm


class InfoboxForm(BootstrapModelForm):
    class Meta:
        model = Appointment
        fields = ["start_date", "end_date", "topic", "description", "groups", "place"]
        widgets = {
            'groups': forms.CheckboxSelectMultiple,
        }

    def clean(self):
        self.instance.is_infobox = True
        return super().clean()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fields["start_date"].widget.attrs["class"] = "datetimepicker form-control"
        self.fields["end_date"].widget.attrs["class"] = "datetimepicker form-control"
        self.fields["description"].widget.attrs["rows"] = "5"


class ConferenceForm(BootstrapModelForm):
    class Meta:
        model = Appointment
        fields = ["start_date", "end_date", "topic", "description", "place", "groups"]
        widgets = {
            'groups': forms.CheckboxSelectMultiple,
        }

    def clean(self):
        self.instance.is_conference = True
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
        self.infobox_form = None
        self.edit_infobox_form = None
        self.edit_conference_form = None
        self.conference_form = None

    def dispatch(self, request, *args, **kwargs):
        self.infobox_form = self.get_infobox_form()
        self.edit_infobox_form = self.get_edit_infobox_form()
        self.edit_conference_form = self.get_edit_conference_form()
        self.conference_form = self.get_conference_form()
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context())

    def get_infobox_form(self):
        if self.request.method == "POST":
            self.infobox_form = InfoboxForm(data=self.request.POST)
        else:
            self.infobox_form = InfoboxForm()
        return self.infobox_form

    def get_conference_form(self):
        if self.request.method == "POST":
            self.conference_form = ConferenceForm(data=self.request.POST)
        else:
            self.conference_form = ConferenceForm()
        return self.conference_form

    def get_edit_infobox_form(self):
        if self.request.method == "POST":
            self.edit_infobox_form = InfoboxForm(prefix="infobox_edit", data=self.request.POST)
        else:
            self.edit_infobox_form = InfoboxForm(prefix="infobox_edit")
        return self.edit_infobox_form

    def get_edit_conference_form(self):
        if self.request.method == "POST":
            self.edit_conference_form = ConferenceForm(prefix="conference_edit", data=self.request.POST)
        else:
            self.edit_conference_form = ConferenceForm(prefix="conference_edit")
        return self.edit_conference_form

    def get_context(self):
        return {"infobox_form": self.infobox_form, "conference_form": self.conference_form,
                "edit_infobox_form": self.edit_infobox_form, "edit_conference_form": self.edit_conference_form}


def get_users_from_groups(groups):
    users = User.objects.filter(groups_list__in=groups).distinct()
    return users


def send_push_notifications(users, title, message):
    push_service = FCMNotification(api_key=os.environ.get("firebase_token"))
    registration_ids = []
    for user in users:
        if user.profile.device_token is not None:
            registration_ids.append(user.profile.device_token)
    if len(registration_ids) > 0:
        result = push_service.notify_multiple_devices(
            registration_ids=registration_ids, message_title=title, message_body=message, sound="default")
        print(result)


class InfoboxView(LoginRequiredMixin, View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.infobox_form = None
        self.conference_form = None

    def dispatch(self, request, *args, **kwargs):
        self.infobox_form = self.get_infobox_form()
        self.conference_form = self.get_conference_form()
        return super().dispatch(request, *args, **kwargs)

    def get_infobox_form(self):
        if self.request.method == "POST":
            self.infobox_form = InfoboxForm(data=self.request.POST)
        else:
            self.infobox_form = InfoboxForm()
        return self.infobox_form

    def get_conference_form(self):
        if self.request.method == "POST":
            self.conference_form = ConferenceForm(initial=self.request.POST)
        else:
            self.conference_form = ConferenceForm()
        return self.conference_form

    def post(self, request, *args, **kwargs):
        if self.infobox_form.is_valid() is True:
            instance = self.infobox_form.save()
            instance.promoter = request.user
            instance.save()
            users = get_users_from_groups(instance.groups.all())
            send_push_notifications(users, instance.topic, instance.description)
            return HttpResponseRedirect(reverse_lazy("appointment:planning"))
        else:
            return render(request, "appointment/appointment.html", self.get_context())

    def get_context(self):
        return {"infobox_form": self.infobox_form, "conference_form": self.conference_form}


class ConferenceView(LoginRequiredMixin, View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.infobox_form = None
        self.conference_form = None

    def dispatch(self, request, *args, **kwargs):
        self.infobox_form = self.get_infobox_form()
        self.conference_form = self.get_conference_form()
        return super().dispatch(request, *args, **kwargs)

    def get_infobox_form(self):
        if self.request.method == "POST":
            self.infobox_form = InfoboxForm(initial=self.request.POST)
        else:
            self.infobox_form = InfoboxForm()
        return self.infobox_form

    def get_conference_form(self):
        if self.request.method == "POST":
            self.conference_form = ConferenceForm(data=self.request.POST)
        else:
            self.conference_form = ConferenceForm()
        return self.conference_form

    def post(self, request, *args, **kwargs):
        if self.conference_form.is_valid() is True:
            instance = self.conference_form.save()
            instance.promoter = request.user
            instance.save()
            users = get_users_from_groups(instance.groups.all())
            send_push_notifications(users, instance.topic, instance.description)
            return HttpResponseRedirect(reverse_lazy("appointment:planning"))
        else:
            return render(request, "appointment/appointment.html", self.get_context())

    def get_context(self):
        return {"infobox_form": self.infobox_form, "conference_form": self.conference_form}


class InfoboxUpdateView(LoginRequiredMixin, View):
    def __init__(self):
        super().__init__()
        self.edit_infobox_form = None
        self.edit_conference_form = None
        self.object = None
        self.infobox_form = None
        self.conference_form = None

    def dispatch(self, request, *args, **kwargs):
        self.object = get_object_or_404(Appointment, pk=self.kwargs.get("pk"))
        self.edit_infobox_form = self.get_edit_infobox_form()
        self.edit_conference_form = self.get_edit_conference_form()
        self.infobox_form = self.get_infobox_form()
        self.conference_form = self.get_conference_form()
        print("call detected !")
        return super().dispatch(request, *args, **kwargs)

    def get_edit_infobox_form(self):
        if self.request.method == "POST":
            self.edit_infobox_form = InfoboxForm(prefix="infobox_edit", data=self.request.POST, instance=self.object)
        else:
            self.edit_infobox_form = InfoboxForm(prefix="infobox_edit", instance=self.object)
        return self.edit_infobox_form

    def get_edit_conference_form(self):
        if self.request.method == "POST":
            self.edit_conference_form = ConferenceForm(prefix="conference_edit", initial=self.request.POST,
                                                       instance=self.object)
        else:
            self.edit_conference_form = ConferenceForm(prefix="conference_edit", instance=self.object)
        return self.edit_conference_form

    def post(self, request, *args, **kwargs):
        print("akhiiii")
        print(self.object.pk)
        if self.edit_infobox_form.is_valid() is True:
            self.edit_infobox_form.save()
            return HttpResponseRedirect(reverse_lazy("appointment:planning"))
        else:
            print(self.edit_infobox_form.errors)
            return render(request, "appointment/appointment.html", {"edit_infobox_form": self.edit_infobox_form,
                                                                    "edit_conference_form": self.edit_conference_form,
                                                                    "infobox_form": self.infobox_form,
                                                                    "conference_form": self.conference_form
                                                                    })

    def get_infobox_form(self):
        if self.request.method == "POST":
            self.infobox_form = InfoboxForm(initial=self.request.POST)
        else:
            self.infobox_form = InfoboxForm()
        return self.infobox_form

    def get_conference_form(self):
        if self.request.method == "POST":
            self.conference_form = ConferenceForm(initial=self.request.POST)
        else:
            self.conference_form = ConferenceForm()
        return self.conference_form


class ConferenceUpdateView(LoginRequiredMixin, View):
    def __init__(self):
        super().__init__()
        self.edit_conference_form = None
        self.edit_infobox_form = None
        self.object = None
        self.infobox_form = None
        self.conference_form = None

    def dispatch(self, request, *args, **kwargs):
        self.object = get_object_or_404(Appointment, pk=self.kwargs.get("pk"))
        self.edit_conference_form = self.get_edit_conference_form()
        self.edit_infobox_form = self.get_edit_infobox_form()
        self.infobox_form = self.get_infobox_form()
        self.conference_form = self.get_conference_form()
        print("call detected !")
        return super().dispatch(request, *args, **kwargs)

    def get_edit_infobox_form(self):
        if self.request.method == "POST":
            self.edit_infobox_form = InfoboxForm(prefix="infobox_edit", initial=self.request.POST, instance=self.object)
        else:
            self.edit_infobox_form = InfoboxForm(prefix="infobox_edit", instance=self.object)
        return self.edit_infobox_form

    def get_edit_conference_form(self):
        if self.request.method == "POST":
            self.edit_conference_form = ConferenceForm(prefix="conference_edit", data=self.request.POST, instance=self.object)
        else:
            self.edit_conference_form = ConferenceForm(prefix="conference_edit", instance=self.object)
        return self.edit_conference_form

    def post(self, request, *args, **kwargs):
        print("akhiiii")
        print(self.object.pk)
        if self.edit_conference_form.is_valid() is True:
            self.edit_conference_form.save()
            return HttpResponseRedirect(reverse_lazy("appointment:planning"))
        else:
            print(self.edit_conference_form.errors)
            return render(request, "appointment/appointment.html", {"edit_conference_form": self.edit_conference_form,
                                                                    "edit_infobox_form": self.edit_infobox_form,
                                                                    "infobox_form": self.infobox_form,
                                                                    "conference_form": self.conference_form})

    def get_infobox_form(self):
        if self.request.method == "POST":
            self.infobox_form = InfoboxForm(initial=self.request.POST)
        else:
            self.infobox_form = InfoboxForm()
        return self.infobox_form

    def get_conference_form(self):
        if self.request.method == "POST":
            self.conference_form = ConferenceForm(initial=self.request.POST)
        else:
            self.conference_form = ConferenceForm()
        return self.conference_form
