from django.test import TestCase
from mixer.backend.django import mixer
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from subject_area.models import SubjectArea
from subject_area.forms import SubjectAreaForm


class SubjectAreaTestCase(TestCase):
    def setUp(self):
        self.session_user = mixer.blend(User)
        self.client.force_login(self.session_user)

    def test_subject_area_creation(self):
        subject_areas_count = SubjectArea.objects.count()
        data = {"title": "Kardiologie"}
        response = self.client.post(reverse_lazy("subject_area:create"), data=data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(SubjectArea.objects.count(), subject_areas_count+1)

    def test_subject_area_edition(self):
        instance = self.create_subject_area()
        old_title = instance.title
        with mixer.ctx(commit=False):
            new_data = mixer.blend(SubjectArea).__dict__
        response = self.client.post(reverse_lazy("subject_area:edit", kwargs={"pk": instance.pk}), data=new_data)
        instance.refresh_from_db()
        new_title = instance.title
        self.assertEqual(response.status_code, 302)
        self.assertNotEqual(old_title, new_title)
        self.assertEqual(new_title, SubjectArea.objects.first().title)

    @staticmethod
    def create_subject_area():
        with mixer.ctx(commit=False):
            data = mixer.blend(SubjectArea).__dict__
        form = SubjectAreaForm(data=data)
        instance = form.save()
        return instance
