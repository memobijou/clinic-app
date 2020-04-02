from django.test import TestCase
from mixer.backend.django import mixer
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.urls import reverse_lazy
import json
from unittest import mock


class BroadcastTestCase(TestCase):
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

    def test_broadcasting(self):
        broadcast_create_response = self.create_broadcast()
        self.assertEqual(broadcast_create_response.status_code, 201)
        broadcast_id = json.loads(broadcast_create_response.content).get("id")
        broadcast_detail_response = self.client.get(
            reverse_lazy("api_broadcast:broadcast-detail",
                         kwargs={"pk": broadcast_id}))
        self.assertEqual(broadcast_detail_response.status_code, 200)

    def test_push_notifications(self):
        self.create_broadcast()
        # User 1
        account_response_user_1 = self.client.get(
            reverse_lazy("api_account:user-detail",
                         kwargs={"pk": self.session_user.pk}))

        # User 2
        account_response_user_2 = self.client.get(
            reverse_lazy("api_account:user-detail",
                         kwargs={"pk": self.second_user.pk}))

        self.assertEqual(json.loads(account_response_user_2.content).get("profile").get("broadcast_badges"), 1)
        self.assertEqual(json.loads(account_response_user_1.content).get("profile").get("broadcast_badges"), 0)

    @mock.patch('pyfcm.FCMNotification.notify_single_device', return_value={})
    @mock.patch('pyfcm.FCMNotification.notify_multiple_devices', return_value={})
    def create_broadcast(self, x, y):
        broadcast_create_response = self.client.post(
            reverse_lazy("api_broadcast:broadcast-list"), data={"text": "hey", "sender_id": self.session_user.pk})
        return broadcast_create_response

    def test_like_broadcast(self):
        broadcast_create_response = self.create_broadcast()
        broadcast_id = json.loads(broadcast_create_response.content).get("id")
        like_create_response = self.like_broadcast(broadcast_id)
        self.assertEqual(like_create_response.status_code, 201)
        broadcast_detail_response = self.client.get(
            reverse_lazy("api_broadcast:broadcast-detail",
                         kwargs={"pk": broadcast_id}))
        self.assertEqual(json.loads(broadcast_detail_response.content).get("likes_count"), 1)

    @mock.patch('pyfcm.FCMNotification.notify_single_device', return_value={})
    @mock.patch('pyfcm.FCMNotification.notify_multiple_devices', return_value={})
    def like_broadcast(self, broadcast_id, x, y):
        like_create_response = self.client.post(
            reverse_lazy("api_broadcast:likes-list", kwargs={"broadcast_id": broadcast_id}),
            data={"user_id": self.session_user.pk})
        return like_create_response

    def test_comment_broadcast(self):
        broadcast_create_response = self.create_broadcast()
        broadcast_id = json.loads(broadcast_create_response.content).get("id")
        comment_create_response = self.comment_broadcast(broadcast_id)
        self.assertEqual(comment_create_response.status_code, 201)

    @mock.patch('pyfcm.FCMNotification.notify_single_device', return_value={})
    @mock.patch('pyfcm.FCMNotification.notify_multiple_devices', return_value={})
    def comment_broadcast(self, broadcast_id, x, y):
        comment_create_response = self.client.post(
            reverse_lazy("api_broadcast:comments-list", kwargs={"broadcast_id": broadcast_id}),
            data={"sender_id": self.session_user.pk, "text": "Some comment"})
        return comment_create_response
