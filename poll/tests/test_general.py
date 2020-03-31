from django.test import TestCase
from mixer.backend.django import mixer
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.urls import reverse_lazy
import json
from unittest import mock
from datetime import date
from account.models import Profile
from poll.models import Poll


class ProposalTestCase(TestCase):
    def setUp(self):
        self.session_user = mixer.blend(User)
        self.session_user.profile.device_token = "abc"
        self.session_user.save()
        self.client.force_login(self.session_user)
        self.token = Token.objects.create(user=self.session_user).key
        self.client.defaults['HTTP_AUTHORIZATION'] = 'Token ' + self.token

    @classmethod
    def setUpTestData(cls):
        cls.second_user = mixer.blend(User)
        cls.second_user.profile.device_token = "def"
        cls.second_user.save()

    def test_poll_creation(self):
        poll_response = self.create_poll()
        self.assertEqual(poll_response.status_code, 302)
        self.assertEqual(Poll.objects.count(), 1)

    def create_poll(self):
        with mixer.ctx(commit=False):
            data = mixer.blend(Poll, title=mixer.RANDOM).__dict__

        poll_response = self.client.post(reverse_lazy("poll:list"), data=data)
        return poll_response

    @mock.patch('pyfcm.FCMNotification.notify_single_device', return_value={})
    @mock.patch('pyfcm.FCMNotification.notify_multiple_devices', return_value={})
    def test_unpublished_poll_not_listed_in_rest_api(self, x, y):
        self.assertEqual(Poll.objects.count(), 0)
        self.create_poll()
        poll_instance = Poll.objects.first()
        poll_api_response = self.client.get(
            reverse_lazy("api_poll:poll-detail", kwargs={"user_id": self.session_user.id, "id": poll_instance.id}))
        self.assertEqual(poll_api_response.status_code, 404)

    @mock.patch('pyfcm.FCMNotification.notify_single_device', return_value={})
    @mock.patch('pyfcm.FCMNotification.notify_multiple_devices', return_value={})
    def test_published_poll_listed_in_rest_api(self, x, y):
        self.create_poll()
        poll_instance = Poll.objects.first()
        poll_instance.open = True
        poll_instance.save()
        poll_api_response = self.client.get(
            reverse_lazy("api_poll:poll-detail", kwargs={"user_id": self.session_user.id, "id": poll_instance.id}))
        self.assertEqual(poll_api_response.status_code, 200)

    def test_poll_publishment_without_option_not_possibile(self):
        self.create_poll()
        poll_instance = Poll.objects.first()
        poll_id = poll_instance.id
        title = poll_instance.title

        response = self.client.post(
            reverse_lazy("poll:edit", kwargs={"pk": poll_id}), data={"open": True, "title": title})
        self.assertEqual(response.status_code, 200)  # error form

        response = self.client.post(
            reverse_lazy("poll:edit", kwargs={"pk": poll_id}),
            data={"option": "Option 1", "open": True, "title": title})
        self.assertEqual(response.status_code, 302)

        response = self.client.post(
            reverse_lazy("poll:edit", kwargs={"pk": poll_id}), data={"open": True, "title": title})
        self.assertEqual(response.status_code, 302)

        response = self.client.post(
            reverse_lazy(
                "poll:edit", kwargs={"pk": poll_id}), data={"option": "Option 2", "open": True, "title": title})
        self.assertEqual(response.status_code, 302)

    def test_poll_edition_title_required(self):
        self.create_poll()
        poll_id = Poll.objects.first().id
        response = self.client.post(reverse_lazy("poll:edit", kwargs={"pk": poll_id}), data={})
        self.assertEqual(response.status_code, 200)  # error form

    def test_option_cannot_be_deletetd_if_published(self):
        pass
