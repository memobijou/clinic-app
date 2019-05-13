from django.test import TestCase
from mixer.backend.django import mixer
from django.contrib.auth.models import User
from taskmanagement.models import Task, UserTask
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

        users = mixer.cycle(5).blend(User)
        user_ids = [user.pk for user in users]
        users_count += len(user_ids)

        data = {"name": "Task A", "description": "Aufgabenbeschreibung", "groups": groups, "users": user_ids}
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

    def test_task_edition(self):
        users, groups, users_count, tasks_count, data = self.create_task()
        response = self.client.post(reverse_lazy("taskmanagement:new_task"), data=data)
        self.assertEqual(response.status_code, 302)
        task_instance = Task.objects.first()
        removed_user_id = data["users"].pop(0)
        response = self.client.post(reverse_lazy("taskmanagement:edit_task", kwargs={"pk": task_instance.pk}),
                                    data=data)
        self.assertEqual(response.status_code, 302)
        removed_user_queryset = UserTask.objects.filter(task=task_instance, user_id=removed_user_id)
        print(f"removed: {removed_user_queryset}")
        self.assertEqual(removed_user_queryset.count(), 0)

    def create_task(self):
        tasks_count = Task.objects.count()
        group_instances = mixer.cycle(5).blend(Group, users=mixer.RANDOM)
        groups = [group.pk for group in group_instances]

        users_count = 0
        for group in group_instances:
            users_count += group.users.count()

        users = mixer.cycle(5).blend(User)
        user_ids = [user.pk for user in users]
        users_count += len(user_ids)
        data = {"name": "Task", "description": "Aufgabenbeschreibung", "groups": groups, "users": user_ids}
        return users, groups, users_count, tasks_count, data
