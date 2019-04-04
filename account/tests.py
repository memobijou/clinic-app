from django.test import TestCase
from account.models import Profile
from django.contrib.auth.models import User
from mixer.backend.django import mixer
from account.forms import CustomUserCreationForm
from django.urls import reverse_lazy
import sys
from account.models import Group


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
        self.assertEqual(response.status_code, 200)
        self.assertEqual(student.mentor, mentor.pk)

    def test_user_password_changed(self):
        data = {"password1": "Password1¢", "password2": "Password1¢", **self.session_user.__dict__}
        response = self.client.post(reverse_lazy(
            "account:user_edit", kwargs={"pk": self.session_user.pk}), data)
        self.assertEqual(response.status_code, 302)
        self.client.logout()
        self.client.login(username=self.session_user.username, password="Password1¢")
        response = self.client.get(reverse_lazy("account:user_edit", kwargs={"pk": self.session_user.pk}))
        self.assertEqual(response.status_code, 200)

    def test_group_creation(self):
        groups_count = Group.objects.count()
        with mixer.ctx(commit=False):
            data = mixer.blend(Group).__dict__
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
