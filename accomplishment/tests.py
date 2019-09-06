from django.test import TestCase
from django.contrib.auth.models import User
from mixer.backend.django import mixer
import json
from accomplishment.forms import AccomplishmentFormMixin
from accomplishment.models import Accomplishment
from django.urls import reverse_lazy
from subject_area.models import SubjectArea
from rest_framework.authtoken.models import Token


class AccomplishmentTestCase(TestCase):
    def setUp(self):
        self.session_user = mixer.blend(User)
        self.client.force_login(self.session_user)
        self.token = Token.objects.create(user=self.session_user).key
        self.client.defaults['HTTP_AUTHORIZATION'] = 'Token ' + self.token

    def test_accomplishment_creation(self):
        accomplishments_count = Accomplishment.objects.count()
        subject_areas = [instance.pk for instance in mixer.cycle(2).blend(SubjectArea)]

        users = mixer.cycle(2).blend(User)
        i = 0
        for user in users:
            user.profile.subject_area_id = subject_areas[i]
            user.save()
            i += 1

        with mixer.ctx(commit=False):
            data = mixer.blend(Accomplishment, full_score=100).__dict__
            data = {**data, "subject_areas": subject_areas}

        response = self.client.post(reverse_lazy("accomplishment:list"), data)

        instance = Accomplishment.objects.first()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Accomplishment.objects.count(), accomplishments_count+1)
        self.assertEqual(len(users), instance.users.all().count())
        self.assertEqual(len(subject_areas), instance.subject_areas.all().count())

        users_after_accomplishment_creation = mixer.cycle(2).blend(User)

        subject_area_after_accomplishment_creation = mixer.blend(SubjectArea)

        instance.subject_areas.add(subject_area_after_accomplishment_creation)

        i = 0
        for user in users_after_accomplishment_creation:
            user.profile.subject_area = subject_area_after_accomplishment_creation
            user.save()
            i += 1

        instance.refresh_from_db()

        self.assertEqual(len(users)+len(users_after_accomplishment_creation), instance.users.all().count())

    def test_accomplishment_edition(self):
        full_score = 3
        instance = self.create_accomplishment(full_score=full_score)
        subject_areas = instance.subject_areas.all()
        accomplishment_users = set(instance.users.values_list("pk", flat=True))

        with mixer.ctx(commit=False):
            new_data = mixer.blend(Accomplishment).__dict__
            new_data = {**new_data, "subject_areas": [subject_area.pk for subject_area in subject_areas]}

        response = self.client.post(reverse_lazy("accomplishment:edit", kwargs={"pk": instance.pk}), data=new_data)
        self.assertEqual(response.status_code, 302)

        instance.refresh_from_db()

        self.assertEqual(instance.name, new_data.get("name"))
        self.assertEqual(instance.subject_areas.all().count(), subject_areas.count())
        self.assertEqual(set(instance.users.values_list("pk", flat=True)), accomplishment_users)

        # test changing of subject_areas

        new_subject_areas = [subject_area.pk for subject_area in mixer.cycle(3).blend(SubjectArea)]
        new_data["subject_areas"] = new_subject_areas

        new_users = mixer.cycle(3).blend(User)
        i = 0
        for user in new_users:
            user.profile.subject_area_id = new_subject_areas[i]
            user.save()
            i += 1

        response = self.client.post(reverse_lazy("accomplishment:edit", kwargs={"pk": instance.pk}), data=new_data)
        self.assertEqual(response.status_code, 302)
        old_user = next(iter(accomplishment_users))
        response = self.client.get(reverse_lazy("api_accomplishment:accomplishment-detail",
                                                kwargs={"accomplishment_id": instance.pk,
                                                        "user_id": old_user}))

        # hier darf der Nutzer nicht mehr auftauchen, da er nicht mehr zur Fachrichtung dazu gehört

        self.assertEqual(response.status_code, 404, f"{json.loads(response.content)}")

        instance.refresh_from_db()

        self.assertEqual(len(new_subject_areas), instance.subject_areas.all().count())
        self.assertNotEqual(set(instance.users.values_list("pk", flat=True)), accomplishment_users)

        # example user must be user from subject_area because non-subject-areas aren't listed on endpoint

        example_user = instance.subject_areas.first().profiles.first().user

        for i in range(0, full_score):
            response = self.client.put(reverse_lazy("api_accomplishment:accomplishment-incrementation",
                                       kwargs={"user_id": example_user.id, "accomplishment_id": instance.id})
                                       )
            self.assertEqual(response.status_code, 200)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content).get("score"), full_score)
        instance.refresh_from_db()

        new_full_score = 1
        new_data["full_score"] = new_full_score

        response = self.client.post(reverse_lazy("accomplishment:edit", kwargs={"pk": instance.pk}), data=new_data)

        self.assertEqual(response.status_code, 302)

        instance.refresh_from_db()

        self.assertEqual(instance.full_score, new_full_score)

    def test_incrementation_and_decrementation_of_users_accomplishment_score(self):
        full_score = 3
        accomplishment = self.create_accomplishment(full_score=full_score)
        user = accomplishment.users.first()

        response, json_response = self.fetch_user_accomplishment(user.id, accomplishment.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json_response.get("score"), 0)

        for i in range(0, full_score):
            self.client.put(reverse_lazy("api_accomplishment:accomplishment-incrementation",
                            kwargs={"user_id": user.id, "accomplishment_id": accomplishment.id})
                            )
        response, json_response = self.fetch_user_accomplishment(user.id, accomplishment.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json_response.get("score"), full_score)

        response = self.client.put(reverse_lazy("api_accomplishment:accomplishment-incrementation",
                                   kwargs={"user_id": user.id, "accomplishment_id": accomplishment.id})
                                   )

        self.assertEqual(response.status_code, 400)

        for i in range(0, full_score):
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

    def create_accomplishment(self, full_score=1):
        subject_areas = [instance.pk for instance in mixer.cycle(2).blend(SubjectArea)]

        users = mixer.cycle(2).blend(User)
        i = 0
        for user in users:
            user.profile.subject_area_id = subject_areas[i]
            user.save()
            i += 1

        with mixer.ctx(commit=False):
            data = mixer.blend(Accomplishment, full_score=full_score).__dict__
            data = {**data, "subject_areas": subject_areas}

        form = AccomplishmentFormMixin(data=data)
        instance = form.save()
        return instance

    def fetch_user_accomplishment(self, user_id, accomplishment_id):
        response = self.client.get(
            reverse_lazy("api_accomplishment:accomplishment-detail",
                         kwargs={"user_id": user_id, "accomplishment_id": accomplishment_id}))
        json_response = json.loads(response.content)
        return response, json_response
