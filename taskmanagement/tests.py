from django.test import TestCase
from mixer.backend.django import mixer
from django.contrib.auth.models import User
from taskmanagement.models import Task
from django.urls import reverse_lazy
from account.models import Group
# Create your tests here.


class TaskManagementTestCase(TestCase):
    def setUp(self):
        self.session_user = mixer.blend(User)
        self.client.force_login(self.session_user)

    def test_task_creation(self):
        tasks_count = Task.objects.count()
        group_instances = mixer.cycle(5).blend(Group, users=mixer.RANDOM)
        groups = [group.pk for group in group_instances]

        users_count = 0
        for group in group_instances:
            users_count += group.users.count()

        data = {"name": "Task A", "description": "Aufgabenbeschreibung", "groups": groups}
        response = self.client.post(reverse_lazy("taskmanagement:new_task"), data=data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(tasks_count+1, Task.objects.count())

        task_instance = Task.objects.first()

        self.assertEqual(task_instance.groups_list.count(), 5)
        self.assertListEqual(groups, list(task_instance.groups_list.values_list("pk", flat=True)))
        self.assertEqual(task_instance.users.count(), users_count)
        # test if user gets added to task when groups changes
        group_instances[0].users.add(mixer.blend(User))
        self.assertEqual(task_instance.users.count(), users_count+1)
