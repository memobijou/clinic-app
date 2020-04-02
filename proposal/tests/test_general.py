from django.test import TestCase
from mixer.backend.django import mixer
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.urls import reverse_lazy
import json
from unittest import mock
from proposal.models import Proposal, Type
from datetime import date
from account.models import Profile


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

    def test_proposal_creation(self):
        response = self.create_proposal()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(json.loads(response.content).get("confirmed"), None)

    def test_proposal_type_creation_without_title_not_possible(self):
        response = self.client.post(reverse_lazy("proposal:list-type"), data={})
        self.assertEqual(response.status_code, 200)

    def test_proposal_creation_without_type_not_possible(self):
        with mixer.ctx(commit=False):
            data = mixer.blend(Proposal, start_date=mixer.RANDOM, end_date=mixer.RANDOM).__dict__

        data["user"] = self.session_user.id
        print(data)
        response = self.client.post(reverse_lazy("api_proposal:proposal-list",
                                                 kwargs={"user_id": self.session_user.id}), data=data)
        self.assertEqual(response.status_code, 400)

    def test_proposal_creation_without_user_not_possible(self):
        with mixer.ctx(commit=True):
            proposal_type = mixer.blend(Type, title=mixer.RANDOM)

        with mixer.ctx(commit=False):
            data = mixer.blend(Proposal, start_date=mixer.RANDOM, end_date=mixer.RANDOM).__dict__

        data["type"] = proposal_type.id

        print(data)
        response = self.client.post(reverse_lazy("api_proposal:proposal-list",
                                                 kwargs={"user_id": self.session_user.id}), data=data)
        self.assertEqual(response.status_code, 400)

    def create_proposal(self):
        with mixer.ctx(commit=True):
            proposal_type = mixer.blend(Type, title=mixer.RANDOM)

        with mixer.ctx(commit=False):
            data = mixer.blend(Proposal, start_date=mixer.RANDOM, end_date=mixer.RANDOM).__dict__

        data["user"] = self.session_user.id
        data["type"] = proposal_type.id
        print(data)
        response = self.client.post(reverse_lazy("api_proposal:proposal-list",
                                                 kwargs={"user_id": self.session_user.id}), data=data)
        return response

    @mock.patch('pyfcm.FCMNotification.notify_single_device', return_value={})
    @mock.patch('pyfcm.FCMNotification.notify_multiple_devices', return_value={})
    def test_proposal_confirmation_and_decline(self, x, y):
        proposal_response = self.create_proposal().content
        proposal_json_response = json.loads(proposal_response)
        proposal_id = proposal_json_response.get("pk")
        self.assertEqual(proposal_json_response.get("confirmed"), None)

        proposal_edition_response = self.client.post(
            reverse_lazy("proposal:edit", kwargs={"pk": proposal_id}), data={"confirmed": True})
        self.assertEqual(proposal_edition_response.status_code, 302)

        proposal_instance = Proposal.objects.get(id=proposal_id)
        self.assertEqual(proposal_instance.confirmed, True)

        proposal_edition_response = self.client.post(
            reverse_lazy("proposal:edit", kwargs={"pk": proposal_id}), data={"confirmed": False})
        self.assertEqual(proposal_edition_response.status_code, 302)

        proposal_instance = Proposal.objects.get(id=proposal_id)
        self.assertEqual(proposal_instance.confirmed, False)

        proposal_edition_response = self.client.post(
            reverse_lazy("proposal:edit", kwargs={"pk": proposal_id}), data={"confirmed": None})
        self.assertEqual(proposal_edition_response.status_code, 302)

        proposal_instance = Proposal.objects.get(id=proposal_id)
        self.assertEqual(proposal_instance.confirmed, None)

    @mock.patch('pyfcm.FCMNotification.notify_single_device', return_value={})
    @mock.patch('pyfcm.FCMNotification.notify_multiple_devices', return_value={})
    def test_proposal_badges(self, x, y):
        proposal_1_response = self.create_proposal()
        proposal_2_response = self.create_proposal()

        proposal_1_id = json.loads(proposal_1_response.content).get("pk")
        proposal_2_id = json.loads(proposal_2_response.content).get("pk")

        proposal_edition_1_response = self.client.post(
            reverse_lazy("proposal:edit", kwargs={"pk": proposal_1_id}), data={"confirmed": True})
        self.assertEqual(proposal_edition_1_response.status_code, 302)

        proposal_edition_2_response = self.client.post(
            reverse_lazy("proposal:edit", kwargs={"pk": proposal_2_id}), data={"confirmed": True})
        self.assertEqual(proposal_edition_2_response.status_code, 302)

        self.assertEqual(Profile.objects.get(user=self.session_user).proposal_badges, 2)
