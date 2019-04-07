from django.test import TestCase
from django.contrib.auth.models import User
from mixer.backend.django import mixer

from accomplishment.forms import AccomplishmentFormMixin
from accomplishment.models import Accomplishment
from django.urls import reverse_lazy
from account.models import Group


class AccomplishmentTestCase(TestCase):
    def setUp(self):
        session_user = mixer.blend(User)
        self.client.force_login(session_user)

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

    def test_accomplishment_edition(self):
        groups_count, users_count = 2, 5
        groups, users = self.create_groups(amount_users=users_count, amount_groups=groups_count)
        with mixer.ctx(commit=False):
            data = mixer.blend(Accomplishment, full_score=100).__dict__
            data = {**data, "groups": [group.pk for group in groups]}
        accomplishment_form = AccomplishmentFormMixin(data=data)
        instance = accomplishment_form.save()

        new_users_count, new_groups_count = 3, 3
        new_groups, new_users = self.create_groups(amount_users=new_users_count, amount_groups=new_groups_count)

        print(instance.user_accomplishments.count())

        with mixer.ctx(commit=False):
            new_data = mixer.blend(Accomplishment, full_score=100).__dict__
            new_data = {**new_data, "groups": [group.pk for group in new_groups]}
        print(f"hey: {new_data}")
        response = self.client.post(reverse_lazy("accomplishment:edit", kwargs={"pk": instance.pk}), new_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(instance.groups.count(), len(new_groups))
        self.assertEqual(instance.user_accomplishments.count(), users_count+new_users_count)

        print(f"denki: {instance.groups.count()}")

    def create_groups(self, amount_users=1, amount_groups=1):
        users_count = amount_users
        users = mixer.cycle(users_count).blend(User)
        groups_count = amount_groups
        groups = mixer.cycle(groups_count).blend(Group, type="discipline")
        for group in groups:
            for user in users:
                group.users.add(user)
        return groups, users

    def test_increment_users_accomplishment_score(self):
        self.client.post(reverse_lazy("accomplishment:list", kwargs={"user:id": 1, "pk": 1}))
