from django.test import TestCase
from mixer.backend.django import mixer
from django.contrib.auth.models import User
from django.urls import reverse_lazy
import json
from rest_framework import serializers
from messaging.models import TextMessage
from unittest import mock
from account.models import Profile
from messaging.utils import send_push_notification_to_receiver


class MessagingTestCase(TestCase):
    def setUp(self):
        self.session_user = mixer.blend(User)
        self.client.force_login(self.session_user)

    def test_message_sending_rest_api(self):
        user_1 = mixer.blend(User)
        user_2 = mixer.blend(User)
        text_message = "Message"
        response = self.client.post(reverse_lazy(
            "api_messaging:messaging-sending", kwargs={"sender": user_1.pk, "receiver": user_2.pk}),
            data={"message": text_message})
        print(f'hey: {reverse_lazy("api_messaging:messaging-sending", kwargs={"sender": user_1.pk, "receiver": user_2.pk})})')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content).get("message"), text_message)

    def test_latest_sender_message_rest_api(self):
        receiver = mixer.blend(User)
        senders = mixer.cycle(5).blend(User)
        for sender in senders:
            for i in range(0, 3):
                response = self.client.post(reverse_lazy(
                    "api_messaging:messaging-sending", kwargs={"sender": sender.pk, "receiver": receiver.pk}),
                    data={"message": "Text Message"})
                self.assertEqual(response.status_code, 200)
        self.assertEqual(TextMessage.objects.count(), 15)
        response = self.client.get(reverse_lazy("api_messaging:receiver_messaging-latest-sender",
                                                kwargs={"receiver": receiver.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content).get("count"), 5)

        for row in json.loads(response.content).get("results"):
            sender_created_datetime = row.get("created_datetime")
            sender_messages = TextMessage.objects.filter(
                sender=row.get("sender").get("pk")).order_by("-created_datetime")
            self.assertEqual(sender_created_datetime,
                             serializers.DateTimeField().to_representation(sender_messages.first().created_datetime))

    @mock.patch('pyfcm.FCMNotification.notify_single_device', return_value={})
    def test_messaging_push_notification_badges(self, notify_single_device_function):
        sender = mixer.blend(User)
        receiver = mixer.blend(User)
        Profile.objects.filter(user__in=[sender, receiver]).update(device_token="somedevicetoken")

        self.assertEqual(receiver.profile.messaging_badges, 0)

        send_push_notification_to_receiver("Test Message", sender, receiver)

        self.assertEqual(receiver.profile.messaging_badges, 1)
        response = self.client.get(reverse_lazy(
            "api_messaging:messaging-list", kwargs={"receiver": receiver.id, "sender": sender.id}))
        self.assertEqual(response.status_code, 200)
        receiver.refresh_from_db()
        self.assertEqual(receiver.profile.messaging_badges, 0)
