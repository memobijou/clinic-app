from django.test import TestCase
from django.contrib.auth.models import User
from mixer.backend.django import mixer
import json
from accomplishment.forms import AccomplishmentFormMixin
from accomplishment.models import Accomplishment, UserAccomplishment
from django.urls import reverse_lazy
from subject_area.models import SubjectArea, Category
from rest_framework.authtoken.models import Token


class AccomplishmentTestCase(TestCase):
    def setUp(self):
        self.session_user = mixer.blend(User)
        self.client.force_login(self.session_user)
        self.token = Token.objects.create(user=self.session_user).key
        self.client.defaults['HTTP_AUTHORIZATION'] = 'Token ' + self.token

    def test_accomplishment_creation(self):
        accomplishments_count = Accomplishment.objects.count()
        subject_areas = [instance for instance in mixer.cycle(2).blend(SubjectArea)]
        categories = [instance for instance in mixer.cycle(2).blend(Category)]

        category_ids = [category.id for category in categories]

        subject_areas[0].category_set.add(categories[0])
        subject_areas[1].category_set.add(categories[1])

        users = mixer.cycle(2).blend(User)

        i = 0

        for user in users:
            print(f"whaaat: {subject_areas[i].id}")
            user.profile.subject_area = subject_areas[i]
            user.save()
            user.profile.save()
            i += 1

            print(f"hey 2: {user.profile.subject_area}")

        with mixer.ctx(commit=False):
            data = mixer.blend(Accomplishment, name="test", full_score=100).__dict__
            data = {**data, "categories": category_ids}

        response = self.client.post(reverse_lazy("accomplishment:list"), data)
        print(response.content)

        accomplishment = Accomplishment.objects.first()

        print(f"yeso: {SubjectArea.objects.all()}")
        print(f"yeso 2: {Category.objects.all()}")
        print(f"yeso 3: {User.objects.all()}")
        print(f"yeso 4: {UserAccomplishment.objects.all()}")

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Accomplishment.objects.count(), accomplishments_count+1)
        self.assertEqual(len(users), accomplishment.users.all().count())
        #  self.assertEqual(len(subject_areas), accomplishment.subject_areas.all().count())

        users_after_accomplishment_creation = mixer.cycle(2).blend(User)

        subject_area_after_accomplishment_creation = mixer.blend(SubjectArea)

        category_after_accomplishment_creation = mixer.blend(
            Category, subject_area=subject_area_after_accomplishment_creation)

        accomplishment.categories.add(category_after_accomplishment_creation)

        i = 0
        for user in users_after_accomplishment_creation:
            user.profile.subject_area = subject_area_after_accomplishment_creation
            user.save()
            i += 1

        accomplishment.refresh_from_db()

        self.assertEqual(len(users)+len(users_after_accomplishment_creation), accomplishment.users.all().count())

    def test_accomplishment_edition(self):
        full_score = 3
        instance = self.create_accomplishment(full_score=full_score)
        subject_areas = instance.subject_areas.all()
        categories = instance.categories.all()
        accomplishment_users = set(instance.users.values_list("pk", flat=True))

        with mixer.ctx(commit=False):
            new_data = mixer.blend(Accomplishment).__dict__
            new_data = {**new_data, "categories": [category.pk for category in categories]}

        response = self.client.post(reverse_lazy("accomplishment:edit", kwargs={"pk": instance.pk}), data=new_data)
        self.assertEqual(response.status_code, 302)

        instance.refresh_from_db()

        self.assertEqual(instance.name, new_data.get("name"))
        self.assertEqual(instance.categories.all().count(), categories.count())
        self.assertEqual(set(instance.users.values_list("pk", flat=True)), accomplishment_users)

        # test changing of subject_areas

        new_subject_areas = [subject_area for subject_area in mixer.cycle(3).blend(SubjectArea)]

        i = 0

        new_categories = [category for category in mixer.cycle(3).blend(Category)]

        for new_subject_area in new_subject_areas:
            new_categories[i].subject_area = new_subject_area
            new_categories[i].save()

        new_data["categories"] = [new_category.pk for new_category in new_categories]

        new_users = mixer.cycle(3).blend(User)

        i = 0
        for user in new_users:
            user.profile.subject_area = new_subject_areas[i]
            user.save()
            user.profile.save()
            i += 1

        response = self.client.post(reverse_lazy("accomplishment:edit", kwargs={"pk": instance.pk}), data=new_data)
        self.assertEqual(response.status_code, 302)
        print(f"?????? {accomplishment_users}")
        old_user = next(iter(accomplishment_users))
        response = self.client.get(reverse_lazy("api_accomplishment:accomplishment-detail",
                                                kwargs={"accomplishment_id": instance.pk,
                                                        "user_id": old_user}))

        # hier darf der Nutzer nicht mehr auftauchen, da er nicht mehr zur Fachrichtung dazu gehört

        self.assertEqual(response.status_code, 404, f"{json.loads(response.content)}")

        instance.refresh_from_db()

        self.assertEqual(len(new_subject_areas), SubjectArea.objects.filter(
            category__in=instance.categories.all()).count())
        self.assertNotEqual(set(instance.users.values_list("pk", flat=True)), accomplishment_users)

        # example user must be user from subject_area because non-subject-areas aren't listed on endpoint

        example_user = instance.categories.first().subject_area.profiles.first().user

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
        subject_areas = [instance for instance in mixer.cycle(2).blend(SubjectArea)]
        categories = [instance for instance in mixer.cycle(2).blend(Category)]

        category_ids = [instance.pk for instance in categories]

        categories[0].subject_area = subject_areas[0]
        categories[1].subject_area = subject_areas[1]

        categories[0].save()
        categories[1].save()

        users = mixer.cycle(2).blend(User)

        i = 0
        for user in users:
            user.profile.subject_area = subject_areas[i]
            user.save()
            user.profile.save()
            i += 1

        with mixer.ctx(commit=False):
            data = mixer.blend(Accomplishment, full_score=full_score).__dict__
            data = {**data, "categories": category_ids}

        form = AccomplishmentFormMixin(data=data)
        instance = form.save()
        print(f"....----....----.... {instance.users.all()}")
        return instance

    def fetch_user_accomplishment(self, user_id, accomplishment_id):
        response = self.client.get(
            reverse_lazy("api_accomplishment:accomplishment-detail",
                         kwargs={"user_id": user_id, "accomplishment_id": accomplishment_id}))
        json_response = json.loads(response.content)
        return response, json_response
