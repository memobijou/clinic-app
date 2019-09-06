from django.test import TestCase
from mixer.backend.django import mixer
from django.contrib.auth.models import User
from account.models import Profile
from appointment.models import Appointment, DutyRoster
from django.urls import reverse_lazy
from account.models import Group
from appointment.views import send_push_notifications
from unittest import mock
from rest_framework.authtoken.models import Token


class AppointmentTestCase(TestCase):
    def setUp(self):
        self.session_user = mixer.blend(User)
        self.client.force_login(self.session_user)
        self.token = Token.objects.create(user=self.session_user).key
        self.client.defaults['HTTP_AUTHORIZATION'] = 'Token ' + self.token

    def test_conference_creation(self):
        appointments_count = Appointment.objects.count()
        with mixer.ctx(commit=False):
            appointment = mixer.blend(Appointment, is_conference=True, start_date="2019-03-01T01:23",
                                      end_date="2019-03-01T03:23")
            data = appointment.__dict__
        response = self.client.post(reverse_lazy("appointment:new_conference"), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(appointments_count+1, Appointment.objects.count())
        self.assertTrue(Appointment.objects.first().is_conference)

    def test_conference_edition(self):
        appointment = mixer.blend(Appointment, is_conference=True, start_date="2019-03-01T01:23",
                                  end_date="2019-03-01T03:23")
        topic = appointment.topic

        with mixer.ctx(commit=False):
            data = mixer.blend(
                Appointment, is_conference=True, start_date="2019-04-01T01:23", end_date="2019-04-03T03:23").__dict__

        groups = mixer.cycle(5).blend(Group)
        data["groups"] = [group.pk for group in groups]

        data = {f"conference_edit-{k}": v for k, v in data.items()}
        print(data)
        response = self.client.post(reverse_lazy("appointment:edit_conference", kwargs={"pk": appointment.pk}), data)
        self.assertEqual(response.status_code, 302)
        appointment = Appointment.objects.first()
        self.assertNotEqual(appointment.topic, topic)

    def test_conference_deletion(self):
        appointment = mixer.blend(Appointment, is_conference=True, start_date="2019-03-01T01:23",
                                  end_date="2019-03-01T03:23")
        response = self.client.post(reverse_lazy("appointment:delete") + f"?item={appointment.pk}")
        self.assertEqual(Appointment.objects.count(), 0)

    @mock.patch('pyfcm.FCMNotification.notify_single_device', return_value={})
    @mock.patch('pyfcm.FCMNotification.notify_multiple_devices', return_value={})
    def test_appointment_push_notification_badges(
            self, notify_single_device_function, notify_multiple_devices_function):
        users = mixer.cycle(5).blend(User)
        Profile.objects.filter(user__in=users).update(device_token="somedevicetoken")

        for user in users:
            self.assertEqual(user.profile.appointment_badges, 0)

        send_push_notifications(User.objects.all(), "Test notification", "Test Message", "appointment")

        for user in User.objects.filter(id__in=[user.id for user in users]):
            print(f"test: {user.profile.appointment_badges}")
            self.assertEqual(user.profile.appointment_badges, 1)
            response = self.client.get(reverse_lazy("api_appointment:appointment-list", kwargs={"user_id": user.id}))
            self.assertEqual(response.status_code, 200)
            user.refresh_from_db()
            self.assertEqual(user.profile.appointment_badges, 0)


class DutyRosterTestCase(TestCase):
    def setUp(self):
        self.session_user = mixer.blend(User)
        self.client.force_login(self.session_user)
        self.token = Token.objects.create(user=self.session_user).key
        self.client.defaults['HTTP_AUTHORIZATION'] = 'Token ' + self.token

    def test_duty_roster_upload(self):
        year = 2019
        month = 3
        response = self.client.post(reverse_lazy("appointment:duty_roster-list"),
                                    data={"month_input": month, "year_input": year})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(DutyRoster.objects.count(), 1)
        duty_roster_queryset = DutyRoster.objects.filter(calendar_week_date__month=month, calendar_week_date__year=year)
        self.assertEqual(duty_roster_queryset.count(), 1)
