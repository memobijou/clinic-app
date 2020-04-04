from django.test import TestCase
from mixer.backend.django import mixer
from django.contrib.auth.models import User
from account.models import Profile
from appointment.models import Appointment, DutyRoster
from django.urls import reverse_lazy
from account.models import Group
from unittest import mock
from rest_framework.authtoken.models import Token


class AppointmentTestCase(TestCase):
    def setUp(self):
        self.session_user = mixer.blend(User)
        profile = self.session_user.profile
        profile.device_token = "somedevicetoken"
        profile.save()
        self.client.force_login(self.session_user)
        self.token = Token.objects.create(user=self.session_user).key
        self.client.defaults['HTTP_AUTHORIZATION'] = 'Token ' + self.token

    def test_conference_creation(self):
        appointments_count = Appointment.objects.count()
        with mixer.ctx(commit=False):
            appointment = mixer.blend(Appointment, start_date="2019-03-01T01:23",
                                      end_date="2019-03-01T03:23")
            data = appointment.__dict__
        response = self.client.post(reverse_lazy("appointment:new_conference"), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(appointments_count+1, Appointment.objects.count())

    def test_conference_edition(self):
        appointment = mixer.blend(Appointment, start_date="2019-03-01T01:23",
                                  end_date="2019-03-01T03:23")
        topic = appointment.topic

        with mixer.ctx(commit=False):
            data = mixer.blend(
                Appointment, start_date="2019-04-01T01:23", end_date="2019-04-03T03:23").__dict__

        groups = mixer.cycle(5).blend(Group)
        data["groups"] = [group.pk for group in groups]

        data = {f"edit-{k}": v for k, v in data.items()}
        print(data)
        response = self.client.post(reverse_lazy("appointment:edit_conference", kwargs={"pk": appointment.pk}), data)
        self.assertEqual(response.status_code, 302)
        appointment = Appointment.objects.first()
        self.assertNotEqual(appointment.topic, topic)

    def test_conference_deletion(self):
        appointment = mixer.blend(Appointment, start_date="2019-03-01T01:23",
                                  end_date="2019-03-01T03:23")
        response = self.client.post(reverse_lazy("appointment:delete") + f"?item={appointment.pk}")
        self.assertEqual(Appointment.objects.count(), 0)

    @mock.patch('pyfcm.FCMNotification.notify_single_device', return_value={})
    @mock.patch('pyfcm.FCMNotification.notify_multiple_devices', return_value={})
    def test_appointment_push_notification_badges(
            self, x, y):
        self.assertEqual(self.session_user.profile.appointment_badges, 0)
        group = mixer.blend(Group)
        group.users.add(self.session_user)
        with mixer.ctx(commit=False):
            appointment = mixer.blend(Appointment, start_date=mixer.RANDOM, end_date=mixer.RANDOM, topic=mixer.RANDOM,
                                      description=mixer.RANDOM)
            data = appointment.__dict__
        data["groups"] = [group.id]
        response = self.client.post(reverse_lazy("appointment:new_conference"), data)
        self.assertEqual(response.status_code, 302)
        self.session_user.profile.refresh_from_db()
        self.assertEqual(self.session_user.profile.appointment_badges, 1)

        edit_data = {}
        for key, value in data.items():
            edit_data[f'edit-{key}'] = value

        response = self.client.post(reverse_lazy("appointment:edit_conference",
                                                 kwargs={"pk": Appointment.objects.last().pk}), edit_data)

        self.assertEqual(response.status_code, 302)
        self.session_user.profile.refresh_from_db()
        self.assertEqual(self.session_user.profile.appointment_badges, 2)


class DutyRosterTestCase(TestCase):
    def setUp(self):
        self.session_user = mixer.blend(User)
        self.client.force_login(self.session_user)
        self.token = Token.objects.create(user=self.session_user).key
        self.client.defaults['HTTP_AUTHORIZATION'] = 'Token ' + self.token
        profile = self.session_user.profile
        profile.device_token = "somedevicetoken"
        profile.save()

    def test_duty_roster_upload(self):
        year = 2019
        month = 3
        response = self.client.post(reverse_lazy("appointment:duty_roster-list"),
                                    data={"month_input": month, "year_input": year})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(DutyRoster.objects.count(), 1)
        duty_roster_queryset = DutyRoster.objects.filter(calendar_week_date__month=month, calendar_week_date__year=year)
        self.assertEqual(duty_roster_queryset.count(), 1)

    @mock.patch('pyfcm.FCMNotification.notify_single_device', return_value={})
    @mock.patch('pyfcm.FCMNotification.notify_multiple_devices', return_value={})
    def test_duty_roster_badges(self, x, y):
        self.assertEqual(self.session_user.profile.duty_roster_badges, 0)
        year = 2019
        month = 12
        response = self.client.post(reverse_lazy("appointment:duty_roster-list"),
                                    data={"month_input": month, "year_input": year})
        self.assertEqual(response.status_code, 201)
        self.session_user.profile.refresh_from_db()
        self.assertEqual(self.session_user.profile.duty_roster_badges, 1)
