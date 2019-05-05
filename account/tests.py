from django.test import TestCase
from django.contrib.auth.models import User
from mixer.backend.django import mixer
from django.urls import reverse_lazy
from account.models import Group
import json
from django.core.serializers.json import DjangoJSONEncoder


# Create your tests here.
# admitStudent_MissingMandatoryFields_FailToAdmit
from subject_area.models import SubjectArea


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

    def test_user_edition(self):
        device_token = "fajPobo-RVg:APA91bGWzDh5E2MXMRqzrnILuiPpcrbMWxSdI8dl2ninxyZ1hfZ3P6OwpU456XTTkA_osO" \
                       "PyQDC74jsMatafHd7BHjlefYYxuHBOjyagjWuT9Lq85gCnq2Up_vVmMK2pgHBMsJLhr2eo"

        user = mixer.blend(User, is_active=False)
        user.profile.device_token = device_token
        user.save()

        self.assertEqual(user.profile.device_token, device_token)
        self.assertEqual(user.is_active, False)

        response = self.client.post(reverse_lazy("account:user_activation"), data={"item": [user.pk]})
        self.assertEqual(response.status_code, 302)  # redirect to users overview

        user.refresh_from_db()
        self.assertEqual(user.is_active, True)

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
            data = mixer.blend(Group).__dict__
        response = self.client.post(reverse_lazy("account:new_group"), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Group.objects.count(), groups_count+1)
        self.assertIsNotNone(Group.objects.first().color)

    def test_users_assignment_to_group(self):
        group = mixer.blend(Group)
        users = mixer.cycle(5).blend(User)
        print(users)
        data = {**group.__dict__, "users": [user.pk for user in users]}
        group_users_count = group.users.count()
        response = self.client.post(reverse_lazy("account:edit_group", kwargs={"pk": group.pk}), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(group.users.count(), group_users_count+5)

    def test_rest_api_login(self):
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

    def test_rest_api_registration(self):
        password = "@strongPassword"
        device_token = "abjPobo-RVg:APA91bGWzDh5E2MXMRqz3nILuiPpcrbMWxSdI8dl23inxyZ1hfZ3P6OwfU456XTTkA_osOPyQ" \
                       "DC24jsMYtafHd7BHjlefYaxuHBOjyagjWuTfLq85gCnq2Up_vVuMK2pgHBMsJLhr2eo"
        device_token = "fajPobo-RVg:APA91bGWzDh5E2MXMRqzrnILuiPpcrbMWxSdI8dl2ninxyZ1hfZ3P6OwpU456XTTkA_osO" \
                       "PyQDC74jsMatafHd7BHjlefYYxuHBOjyagjWuT9Lq85gCnq2Up_vVmMK2pgHBMsJLhr2eo"
        data = {"username": "test_user", "password": password, "password2": password, "email": "peter@hotmailabc.com",
                "first_name": "Peter", "last_name": "Schmidt",
                "device_token": device_token}

        response = self.client.post(reverse_lazy("api_account:user-registration"), data=data)
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.content)
        self.assertNotEqual(json_response.get("pk"), None)

        new_user = User.objects.get(pk=json_response.get("pk"))
        self.assertEqual(device_token, new_user.profile.device_token)
        self.assertTrue(new_user.check_password(password))
        self.assertNotIn("password", json_response)
        self.assertNotIn("password2", json_response)
        print(f"hello boy: {json_response}")

        # TEST VALIDATIONS

        # Test Existing User error

        response = self.client.post(reverse_lazy("api_account:user-registration"),
                                    data=data)
        self.assertEqual(response.status_code, 400)

        # Test password similar to username error

        data["username"] = "new_user"
        data["email"] = "new_mail@hotmailiey.de"
        test_data = {**data, "password": "new_user", "password2": "new_user"}

        response = self.client.post(reverse_lazy("api_account:user-registration"), test_data)
        self.assertEqual(response.status_code, 400)

        # Test required fields errors

        test_data = {**data}
        test_data.pop("first_name")

        response = self.client.post(reverse_lazy("api_account:user-registration"), data=test_data)
        self.assertEqual(response.status_code, 400)

        test_data = {**data}
        test_data.pop("last_name")

        response = self.client.post(reverse_lazy("api_account:user-registration"), data=test_data)
        self.assertEqual(response.status_code, 400)

        test_data = {**data}
        test_data.pop("email")

        response = self.client.post(reverse_lazy("api_account:user-registration"), data=test_data)
        self.assertEqual(response.status_code, 400)

    def test_rest_api_user_subject_area_assignment(self):
        user = mixer.blend(User)
        subject_area = mixer.blend(SubjectArea)
        user.profile.subject_area = subject_area
        user.save()
        new_subject_area = mixer.blend(SubjectArea)
        print(reverse_lazy("api_account:user-subject-area-assignment", kwargs={"pk": user.pk}))
        response = self.client.put(reverse_lazy("api_account:user-subject-area-assignment", kwargs={"pk": user.pk}),
                                   data={"subject_area": new_subject_area.pk}, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.get(pk=user.pk).profile.subject_area.title, new_subject_area.title)

    def test_rest_api_user_device_token_assignment(self):
        user = mixer.blend(User)
        old_device_token = "OLDDEVICETOKEN"
        user.profile.device_token = old_device_token
        user.save()
        new_device_token = "NEWDEVICETOKEN"
        print(reverse_lazy("api_account:user-device-token-assignment", kwargs={"pk": user.pk}))
        response = self.client.put(reverse_lazy("api_account:user-device-token-assignment", kwargs={"pk": user.pk}),
                                   data={"device_token": new_device_token}, content_type="application/json")
        print(json.loads(response.content))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.get(pk=user.pk).profile.device_token, new_device_token)
