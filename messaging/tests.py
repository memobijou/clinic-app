from django.test import TestCase
from mixer.backend.django import mixer
from django.contrib.auth.models import User
from django.urls import reverse_lazy
import json
# Create your tests here.


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
