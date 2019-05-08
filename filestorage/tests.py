from django.test import TestCase
from django.urls import reverse_lazy
# Create your tests here.
from filestorage.models import FileDirectory
from mixer.backend.django import mixer
from django.contrib.auth.models import User
from filestorage.models import File


class FilestorageTestCase(TestCase):
    def setUp(self):
        self.session_user = mixer.blend(User)
        self.client.force_login(self.session_user)

    def test_directory_creation(self):
        response = self.client.post(reverse_lazy("filestorage:tree"), data={"name": "directory"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(FileDirectory.objects.count(), 1)

    def test_child_directory_creation(self):
        parent_directory = FileDirectory.objects.create(name="directory")
        response = self.client.post(
            reverse_lazy("filestorage:child_tree", kwargs={"parent_directory_pk": parent_directory.pk}),
            data={"name": "sub_directory"})
        self.assertEqual(response.status_code, 302)
        parent_directory.refresh_from_db()
        print(FileDirectory.objects.last().parent)
        self.assertEqual(parent_directory.child_directories.count(), 1)

    def test_file_upload(self):
        pass

    def test_file_and_directory_deletion(self):
        directory = FileDirectory.objects.create(name="Directory")
        file = File.objects.create(parent_directory=directory)
        file_2 = File.objects.create(parent_directory=directory)
        response = self.client.post(reverse_lazy("filestorage:delete_files", kwargs={"directory_pk": directory.pk}),
                                    data={"item": [file.pk, file_2.pk]})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(directory.files.count(), 0)
        response = self.client.post(reverse_lazy("filestorage:delete_files", kwargs={"directory_pk": directory.pk}),
                                    data={"directory": [directory.pk]})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(FileDirectory.objects.count(), 0)

    def test_directory_deletion_not_allowed_if_files_and_subidrectories(self):
        directory = FileDirectory.objects.create(name="Directory")
        file = File.objects.create(parent_directory=directory)
        file_2 = File.objects.create(parent_directory=directory)
        sub_directory = FileDirectory.objects.create(name="Directory", parent=directory)
        response = self.client.post(reverse_lazy("filestorage:delete_files", kwargs={"directory_pk": directory.pk}),
                                    data={"directory": [directory.pk]})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(FileDirectory.objects.filter(parent__isnull=True).count(), 1)

    def test_file_edition(self):
        directory = FileDirectory.objects.create(name="Directory")
        file = File.objects.create(parent_directory=directory)
        new_file_name = "new_file_name.pdf"
        response = self.client.post(reverse_lazy("filestorage:file_upload_edit", kwargs={"file_pk": file.pk}),
                                    data={"version": 1.3, "name": new_file_name})
        self.assertEqual(response.status_code, 201)
        file.refresh_from_db()
        self.assertEqual(file.file.name, new_file_name)
