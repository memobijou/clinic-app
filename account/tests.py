from django.test import TestCase
from django.contrib.auth.models import User
from mixer.backend.django import mixer
from django.urls import reverse_lazy
from account.models import Group
import json


# Create your tests here.
# admitStudent_MissingMandatoryFields_FailToAdmit
class UserTestCase(TestCase):
    def setUp(self):
        self.session_user = mixer.blend(User)
        self.client.force_login(self.session_user)

    def test_user_creation(self):
        users_count = User.objects.count()
        with mixer.ctx(commit=False):
            user = mixer.blend(User)
            user_data = user.__dict__
            user_data["password1"] = "Password1¢"
            user_data["password2"] = "Password1¢"
        response = self.client.post(reverse_lazy("account:create_user"), user_data)
        self.assertEqual(response.status_code, 302)  # redirect to users overview
        self.assertEqual(User.objects.count(), users_count+1)

    def test_user_can_have_mentor(self):
        student = self.session_user
        mentor = mixer.blend(User)
        data = student.__dict__
        data["mentor"] = mentor.pk
        response = self.client.post(reverse_lazy("account:user_profile", kwargs={"pk": student.pk}), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(student.mentor, mentor.pk)

    def test_user_password_changed(self):
        data = {"new_password1": "Password1¢", "new_password2": "Password1¢", **self.session_user.__dict__}
        response = self.client.post(reverse_lazy(
            "account:change_user_password", kwargs={"pk": self.session_user.pk}), data)
        self.assertEqual(response.status_code, 302)
        self.client.logout()
        self.client.login(username=self.session_user.username, password="Password1¢")
        response = self.client.get(reverse_lazy("account:change_user_password", kwargs={"pk": self.session_user.pk}))
        self.assertEqual(response.status_code, 302)

    def test_group_creation(self):
        groups_count = Group.objects.count()
        with mixer.ctx(commit=False):
            data = mixer.blend(Group, type="discipline").__dict__
        response = self.client.post(reverse_lazy("account:new_group"), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Group.objects.count(), groups_count+1)

    def test_users_assignment_to_group(self):
        group = mixer.blend(Group)
        users = mixer.cycle(5).blend(User)
        print(users)
        data = {**group.__dict__, "users": [user.pk for user in users]}
        group_users_count = group.users.count()
        response = self.client.post(reverse_lazy("account:edit_group", kwargs={"pk": group.pk}), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(group.users.count(), group_users_count+5)

    def test_login_api(self):
        user = mixer.blend(User)
        password = "Password1¢"
        user.set_password(password)
        user.save()
        response = self.client.post(reverse_lazy("api_account:user-login"),
                                    data={"username": user.username, "password": password})
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.content)
        self.assertEqual(user.pk, json_response.get("pk"))

        response = self.client.post(reverse_lazy("api_account:user-login"),
                                    data={"username": user.username, "password": "WRONG PASSWORD"})
        self.assertEqual(response.status_code, 400)
