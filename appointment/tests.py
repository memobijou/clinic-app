from django.test import TestCase
from mixer.backend.django import mixer
from django.contrib.auth.models import User
from appointment.models import Appointment, DutyRoster
from django.urls import reverse_lazy
from account.models import Group


class AppointmentTestCase(TestCase):
    def setUp(self):
        self.session_user = mixer.blend(User)
        self.client.force_login(self.session_user)

    def test_infobox_creation(self):
        appointments_count = Appointment.objects.count()
        with mixer.ctx(commit=False):
            appointment = mixer.blend(Appointment, is_infobox=True, start_date="2019-03-01T01:23",
                                      end_date="2019-03-01T03:23")
            data = appointment.__dict__
        response = self.client.post(reverse_lazy("appointment:new_infobox"), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(appointments_count+1, Appointment.objects.count())
        self.assertTrue(Appointment.objects.first().is_infobox)

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

    def test_infobox_edition(self):
        appointment = mixer.blend(Appointment, is_infobox=True, start_date="2019-03-01T01:23",
                                  end_date="2019-03-01T03:23")
        topic = appointment.topic

        with mixer.ctx(commit=False):
            data = mixer.blend(
                Appointment, is_infobox=True, start_date="2019-04-01T01:23", end_date="2019-04-03T03:23").__dict__

        groups = mixer.cycle(5).blend(Group)
        data["groups"] = [group.pk for group in groups]

        data = {f"infobox_edit-{k}": v for k, v in data.items()}
        response = self.client.post(reverse_lazy("appointment:edit_infobox", kwargs={"pk": appointment.pk}), data)
        self.assertEqual(response.status_code, 302)
        appointment = Appointment.objects.first()
        self.assertNotEqual(appointment.topic, topic)

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

    def test_infobox_deletion(self):
        appointment = mixer.blend(Appointment, is_infobox=True, start_date="2019-03-01T01:23",
                                  end_date="2019-03-01T03:23")
        response = self.client.post(reverse_lazy("appointment:delete") + f"?item={appointment.pk}")
        self.assertEqual(Appointment.objects.count(), 0)


class DutyRosterTestCase(TestCase):
    def setUp(self):
        self.session_user = mixer.blend(User)
        self.client.force_login(self.session_user)

    def test_duty_roster_upload(self):
        year = 2019
        month = 3
        response = self.client.post(reverse_lazy("appointment:duty_roster-list"),
                                    data={"month_input": month, "year_input": year})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(DutyRoster.objects.count(), 1)
        duty_roster_queryset = DutyRoster.objects.filter(calendar_week_date__month=month, calendar_week_date__year=year)
        self.assertEqual(duty_roster_queryset.count(), 1)
