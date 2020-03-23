from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.test import TestCase, TransactionTestCase, SimpleTestCase
from mixer.backend.django import mixer
from django.contrib.auth.models import User
from django.urls import reverse_lazy
import json
from rest_framework import serializers
from filestorage.models import File, FileUserHistory, FileDirectory
from filestorage.serializers import send_file_messages_through_firebase
from messaging.models import TextMessage
from unittest import mock
from account.models import Profile
from rest_framework.authtoken.models import Token
from rest_framework.test import APIRequestFactory


class FilestorageTestCase(TestCase):
    def setUp(self):
        self.session_user = mixer.blend(User)
        self.client.force_login(self.session_user)
        self.token = Token.objects.create(user=self.session_user).key
        self.client.defaults['HTTP_AUTHORIZATION'] = 'Token ' + self.token

    @classmethod
    def setUpTestData(cls):
        cls.file = mixer.blend(File)
        parent_directory = cls.file.parent_directory
        parent_directory.announcement = True
        parent_directory.save()
        cls.second_user = mixer.blend(User)

    def test_pushes(self):
        self.send_pushes()
        self.assertEqual(self.file.fileuserhistory_set.filter(user=self.session_user).first().unread_notifications, 3)
        self.assertEqual(self.file.fileuserhistory_set.filter(user=self.second_user).first().unread_notifications, 3)
        print(f'brauu 1: {FileUserHistory.objects.count()}')

    @mock.patch('pyfcm.FCMNotification.notify_single_device', return_value={})
    @mock.patch('pyfcm.FCMNotification.notify_multiple_devices', return_value={})
    def send_pushes(self, notify_single_device_function, notify_multiple_devices_function):
        send_file_messages_through_firebase(self.file, is_new=False)
        send_file_messages_through_firebase(self.file, is_new=False)
        send_file_messages_through_firebase(self.file, is_new=False)

    def test_unread_notifications_decrementation(self):
        self.send_pushes()
        print(f'brauu 2: {FileUserHistory.objects.count()}')
        response_user_1 = self.client.get(
            reverse_lazy("api_filestorage:directories-detail",
                         kwargs={"user_id": self.session_user.pk, "pk": self.file.parent_directory.pk}))
        self.assertEqual(response_user_1.status_code, 200)
        response_user_2 = self.client.get(
            reverse_lazy("api_filestorage:directories-detail",
                         kwargs={"user_id": self.second_user.pk, "pk": self.file.parent_directory.pk}))
        self.assertEqual(response_user_1.status_code, 200)
        self.assertEqual(response_user_2.status_code, 200)
        self.assertEqual(FileUserHistory.objects.get(user=self.session_user).unread_notifications, 0)
        self.assertEqual(FileUserHistory.objects.get(user=self.second_user).unread_notifications, 0)

    @mock.patch('pyfcm.FCMNotification.notify_single_device', return_value={})
    @mock.patch('pyfcm.FCMNotification.notify_multiple_devices', return_value={})
    def test_hierarchy_pushes(self, x, y):
        parent_id = self.file.parent_directory_id
        amount_directories = 5
        for i in range(amount_directories):
            new_directory = mixer.blend(FileDirectory, parent_id=parent_id, announcement=True)
            new_file = mixer.blend(File, parent_directory_id=new_directory.id)
            parent_id = new_directory.id
            send_file_messages_through_firebase(new_file, is_new=False)

        account_response_user_1 = self.client.get(
            reverse_lazy("api_account:user-detail",
                         kwargs={"pk": self.session_user.pk}))

        self.assertEqual(json.loads(account_response_user_1.content).get("profile").get("filestorage_badges"),
                         amount_directories)

        account_response_user_2 = self.client.get(
            reverse_lazy("api_account:user-detail",
                         kwargs={"pk": self.second_user.pk}))

        self.assertEqual(json.loads(account_response_user_2.content).get("profile").get("filestorage_badges"),
                         amount_directories)

        response_user_1 = self.client.get(
            reverse_lazy("api_filestorage:directories-detail",
                         kwargs={"user_id": self.session_user.pk, "pk": 8}))

        self.assertEqual(response_user_1.status_code, 200)

        account_response_user_1 = self.client.get(
            reverse_lazy("api_account:user-detail", kwargs={"pk": self.session_user.pk}))

        self.assertEqual(json.loads(account_response_user_1.content).get("profile").get("filestorage_badges"),
                         amount_directories-1)

        account_response_user_2 = self.client.get(
            reverse_lazy("api_account:user-detail", kwargs={"pk": self.second_user.pk}))

        self.assertEqual(json.loads(account_response_user_2.content).get("profile").get("filestorage_badges"),
                         amount_directories)

    @mock.patch('pyfcm.FCMNotification.notify_single_device', return_value={})
    @mock.patch('pyfcm.FCMNotification.notify_multiple_devices', return_value={})
    def test_show_notifications_for_child_directories(self, x, y):
        parent = self.file.parent_directory
        amount_directories = 20  # hier kann ich peformance testen einfach inkrementieren
        new_directory = None
        for i in range(amount_directories):
            new_directory = mixer.blend(FileDirectory, parent=parent, announcement=True)
            new_file = mixer.blend(File, parent_directory=new_directory)
            parent = new_directory
            send_file_messages_through_firebase(new_file, is_new=False)

        print(f"brrrruuuuh: {new_directory.pk}")

        response_user_1 = self.client.get(
            reverse_lazy("api_filestorage:directories-detail",
                         kwargs={"user_id": self.session_user.pk, "pk": new_directory.pk-3}))

        response_user_1_json = json.loads(response_user_1.content)

        self.assertEqual(response_user_1_json.get("child_directories")[0].get("unread_notifications"), 3)

        response_user_1 = self.client.get(
            reverse_lazy("api_filestorage:directories-detail",
                         kwargs={"user_id": self.session_user.pk, "pk": new_directory.pk-2}))

        response_user_1_json = json.loads(response_user_1.content)
        print(f"bam: {response_user_1_json}")
        self.assertEqual(response_user_1_json.get("child_directories")[0].get("unread_notifications"), 2)

        response_user_1 = self.client.get(
            reverse_lazy("api_filestorage:directories-detail",
                         kwargs={"user_id": self.session_user.pk, "pk": new_directory.pk-3}))

        response_user_1_json = json.loads(response_user_1.content)

        self.assertEqual(response_user_1_json.get("child_directories")[0].get("unread_notifications"), 2)

        account_response_user_1 = self.client.get(
            reverse_lazy("api_account:user-detail", kwargs={"pk": self.session_user.pk}))

        self.assertEqual(json.loads(account_response_user_1.content).get("profile").get("filestorage_badges"),
                         amount_directories-2)

        response_user_1 = self.client.get(
            reverse_lazy("api_filestorage:directories-detail",
                         kwargs={"user_id": self.session_user.pk, "pk": new_directory.pk-1}))

        response_user_1_json = json.loads(response_user_1.content)
        print(f"bam: {response_user_1_json}")
        self.assertEqual(response_user_1_json.get("child_directories")[0].get("unread_notifications"), 1)

        response_user_1 = self.client.get(
            reverse_lazy("api_filestorage:directories-detail",
                         kwargs={"user_id": self.session_user.pk, "pk": new_directory.pk-2}))

        response_user_1_json = json.loads(response_user_1.content)
        print(f"bam: {response_user_1_json}")
        self.assertEqual(response_user_1_json.get("child_directories")[0].get("unread_notifications"), 1)

        response_user_1 = self.client.get(
            reverse_lazy("api_filestorage:directories-detail",
                         kwargs={"user_id": self.session_user.pk, "pk": new_directory.pk-3}))

        response_user_1_json = json.loads(response_user_1.content)
        print(f"bam: {response_user_1_json}")
        self.assertEqual(response_user_1_json.get("child_directories")[0].get("unread_notifications"), 1)

        account_response_user_1 = self.client.get(
            reverse_lazy("api_account:user-detail", kwargs={"pk": self.session_user.pk}))

        self.assertEqual(json.loads(account_response_user_1.content).get("profile").get("filestorage_badges"),
                         amount_directories-3)
