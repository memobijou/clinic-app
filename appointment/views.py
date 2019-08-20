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


class InfoboxFormMixin(BootstrapModelFormMixin):
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


class ConferenceFormMixin(BootstrapModelFormMixin):
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
        self.edit_infobox_form = None
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
            self.edit_conference_form = ConferenceFormMixin(prefix="conference_edit", data=self.request.POST)
        else:
            self.edit_conference_form = ConferenceFormMixin(prefix="conference_edit")
        return self.edit_conference_form

    def get_context(self):
        return {"conference_form": self.conference_form, "edit_conference_form": self.edit_conference_form}


def get_users_from_groups(groups):
    users = User.objects.filter(groups_list__in=groups).distinct()
    return users


def send_push_notifications(users, title, message, category):
    if os.environ.get("firebase_token"):
        push_service = FCMNotification(api_key=os.environ.get("firebase_token"))
        registration_ids = []
        badges_totals = {}
        users = users.prefetch_related("profile")
        push_user_ids = []

        for user in users:
            if user.profile.device_token is not None:
                registration_ids.append(user.profile.device_token)
                push_user_ids.append(user.id)

        Profile.objects.filter(user_id__in=push_user_ids).update(appointment_badges=F("appointment_badges") + 1)

        for user in User.objects.filter(id__in=push_user_ids):
            if user.profile.device_token is not None:
                badges_totals[user.profile.device_token] = user.profile.get_total_badges()

        if len(registration_ids) > 0:
            try:
                if len(message) > 20:
                    message = message[:20] + "..."

                for registration_id in registration_ids:
                    push_service.notify_single_device(
                        registration_id=registration_id, message_title=title, message_body=message, sound="default",
                        data_message={"category": category}, badge=badges_totals.get(registration_id)
                    )

                # silent push
                push_service.notify_multiple_devices(
                    registration_ids=registration_ids,
                    data_message={"category": category}, content_available=True
                )
            except (AuthenticationError, FCMServerError, InvalidDataError, InternalPackageError) as e:
                print(e)


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
            self.infobox_form = InfoboxFormMixin(data=self.request.POST)
        else:
            self.infobox_form = InfoboxFormMixin()
        return self.infobox_form

    def get_conference_form(self):
        if self.request.method == "POST":
            self.conference_form = ConferenceFormMixin(initial=self.request.POST)
        else:
            self.conference_form = ConferenceFormMixin()
        return self.conference_form

    def post(self, request, *args, **kwargs):
        if self.infobox_form.is_valid() is True:
            instance = self.infobox_form.save()
            instance.promoter = request.user
            instance.save()
            users = get_users_from_groups(instance.groups.all())
            send_push_notifications(users, instance.topic, instance.description, "infobox")
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
            self.infobox_form = InfoboxFormMixin(initial=self.request.POST)
        else:
            self.infobox_form = InfoboxFormMixin()
        return self.infobox_form

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
            send_push_notifications(users, instance.topic, instance.description, "conference")
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
        return super().dispatch(request, *args, **kwargs)

    def get_edit_infobox_form(self):
        if self.request.method == "POST":
            self.edit_infobox_form = InfoboxFormMixin(prefix="infobox_edit", data=self.request.POST,
                                                      instance=self.object)
        else:
            self.edit_infobox_form = InfoboxFormMixin(prefix="infobox_edit", instance=self.object)
        return self.edit_infobox_form

    def get_edit_conference_form(self):
        if self.request.method == "POST":
            self.edit_conference_form = ConferenceFormMixin(prefix="conference_edit", initial=self.request.POST,
                                                            instance=self.object)
        else:
            self.edit_conference_form = ConferenceFormMixin(prefix="conference_edit", instance=self.object)
        return self.edit_conference_form

    def post(self, request, *args, **kwargs):
        if self.edit_infobox_form.is_valid() is True:
            self.edit_infobox_form.save()
            users = get_users_from_groups(self.object.groups.all())
            send_push_notifications(users, self.object.topic, self.object.description, "infobox")
            return HttpResponseRedirect(reverse_lazy("appointment:planning"))
        else:
            print(f"king: {self.edit_infobox_form.errors}")
            return render(request, "appointment/appointment.html", {"edit_infobox_form": self.edit_infobox_form,
                                                                    "edit_conference_form": self.edit_conference_form,
                                                                    "infobox_form": self.infobox_form,
                                                                    "conference_form": self.conference_form
                                                                    })

    def get_infobox_form(self):
        if self.request.method == "POST":
            self.infobox_form = InfoboxFormMixin(initial=self.request.POST)
        else:
            self.infobox_form = InfoboxFormMixin()
        return self.infobox_form

    def get_conference_form(self):
        if self.request.method == "POST":
            self.conference_form = ConferenceFormMixin(initial=self.request.POST)
        else:
            self.conference_form = ConferenceFormMixin()
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
        return super().dispatch(request, *args, **kwargs)

    def get_edit_infobox_form(self):
        if self.request.method == "POST":
            self.edit_infobox_form = InfoboxFormMixin(prefix="infobox_edit", initial=self.request.POST, instance=self.object)
        else:
            self.edit_infobox_form = InfoboxFormMixin(prefix="infobox_edit", instance=self.object)
        return self.edit_infobox_form

    def get_edit_conference_form(self):
        if self.request.method == "POST":
            self.edit_conference_form = ConferenceFormMixin(prefix="conference_edit", data=self.request.POST, instance=self.object)
        else:
            self.edit_conference_form = ConferenceFormMixin(prefix="conference_edit", instance=self.object)
        return self.edit_conference_form

    def post(self, request, *args, **kwargs):
        if self.edit_conference_form.is_valid() is True:
            self.edit_conference_form.save()
            users = get_users_from_groups(self.object.groups.all())
            send_push_notifications(users, self.object.topic, self.object.description, "conference")
            return HttpResponseRedirect(reverse_lazy("appointment:planning"))
        else:
            return render(request, "appointment/appointment.html", {"edit_conference_form": self.edit_conference_form,
                                                                    "edit_infobox_form": self.edit_infobox_form,
                                                                    "infobox_form": self.infobox_form,
                                                                    "conference_form": self.conference_form})

    def get_infobox_form(self):
        if self.request.method == "POST":
            self.infobox_form = InfoboxFormMixin(initial=self.request.POST)
        else:
            self.infobox_form = InfoboxFormMixin()
        return self.infobox_form

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
