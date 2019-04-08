from django.test import TestCase
from django.contrib.auth.models import User
from mixer.backend.django import mixer
import json
from accomplishment.forms import AccomplishmentFormMixin
from accomplishment.models import Accomplishment
from django.urls import reverse_lazy
from account.models import Group


class AccomplishmentTestCase(TestCase):
    def setUp(self):
        self.session_user = mixer.blend(User)
        self.client.force_login(self.session_user)

    def test_accomplishment_creation(self):
        accomplishments_count = Accomplishment.objects.count()
        groups_count = 2
        users_count = 5
        groups, _ = self.create_groups(amount_users=users_count, amount_groups=groups_count)

        with mixer.ctx(commit=False):
            data = mixer.blend(Accomplishment, full_score=100).__dict__
            data = {**data, "groups": [group.pk for group in groups]}

        response = self.client.post(reverse_lazy("accomplishment:list"), data)
        instance = Accomplishment.objects.first()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Accomplishment.objects.count(), accomplishments_count+1)
        self.assertEqual(instance.groups.count(), groups_count)
        self.assertEqual(instance.user_accomplishments.count(), users_count)
        Accomplishment.objects.create()
        Accomplishment.objects.create()
        print(f"DANN: {Accomplishment.objects.count()}")

    def test_accomplishment_edition(self):
        instance, groups, users = self.create_accomplishment()
        new_users_count, new_groups_count = 3, 3
        new_groups, new_users = self.create_groups(amount_users=new_users_count, amount_groups=new_groups_count)

        with mixer.ctx(commit=False):
            new_data = mixer.blend(Accomplishment, full_score=100).__dict__
            new_data = {**new_data, "groups": [group.pk for group in new_groups]}

        response = self.client.post(reverse_lazy("accomplishment:edit", kwargs={"pk": instance.pk}), new_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(instance.groups.count(), len(new_groups))
        self.assertEqual(instance.user_accomplishments.count(), len(users)+len(new_users))

    def create_groups(self, amount_users=1, amount_groups=1):
        users_count = amount_users
        users = mixer.cycle(users_count).blend(User)
        groups_count = amount_groups
        groups = mixer.cycle(groups_count).blend(Group, type="discipline")
        for group in groups:
            for user in users:
                group.users.add(user)
        return groups, users

    def create_accomplishment(self, amount_users=1, amount_groups=1):
        groups, users = self.create_groups(amount_users=amount_users, amount_groups=amount_groups)
        with mixer.ctx(commit=False):
            data = mixer.blend(Accomplishment, full_score=100).__dict__
            data = {**data, "groups": [group.pk for group in groups]}
        accomplishment_form = AccomplishmentFormMixin(data=data)
        instance = accomplishment_form.save()
        return instance, groups, users

    def test_incrementation_and_decrementation_of_users_accomplishment_score(self):
        accomplishment, groups, users = self.create_accomplishment(amount_users=5, amount_groups=1)
        user = users[0]

        response, json_response = self.fetch_user_accomplishment(user.id, accomplishment.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json_response.get("score"), 0)

        for i in range(0, 20):
            self.client.put(reverse_lazy("api_accomplishment:accomplishment-incrementation",
                            kwargs={"user_id": user.id, "accomplishment_id": accomplishment.id})
                            )
        response, json_response = self.fetch_user_accomplishment(user.id, accomplishment.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json_response.get("score"), 100)
        response = self.client.put(reverse_lazy("api_accomplishment:accomplishment-incrementation",
                                   kwargs={"user_id": user.id, "accomplishment_id": accomplishment.id})
                                   )
        self.assertEqual(response.status_code, 400)

        for i in range(0, 20):
            self.client.put(reverse_lazy("api_accomplishment:accomplishment-decrementation",
                            kwargs={"user_id": user.id, "accomplishment_id": accomplishment.id})
                            )

        response, json_response = self.fetch_user_accomplishment(user.id, accomplishment.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json_response.get("score"), 0)

        response = self.client.put(reverse_lazy("api_accomplishment:accomplishment-decrementation",
                                   kwargs={"user_id": user.id, "accomplishment_id": accomplishment.id})
                                   )

        self.assertEqual(response.status_code, 400)

    def fetch_user_accomplishment(self, user_id, accomplishment_id):
        response = self.client.get(
            reverse_lazy("api_accomplishment:accomplishment-detail",
                         kwargs={"user_id": user_id, "accomplishment_id": accomplishment_id}))
        json_response = json.loads(response.content)
        return response, json_response
