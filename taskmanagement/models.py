from django.contrib.auth.models import User
from django.db import models

# Create your models here.


class Task(models.Model):
    name = models.CharField(null=True, blank=False, max_length=200)
    users = models.ManyToManyField(to=User, blank=True, through="taskmanagement.UserTask",
                                   related_name="tasks", verbose_name="Benutzer")

    def __str__(self):
        return f"{self.name}"

    class Meta:
        ordering = ("pk", )


class UserTask(models.Model):
    task = models.ForeignKey("taskmanagement.Task", null=True, on_delete=models.SET_NULL, related_name="usertasks")
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="usertasks")
    completed = models.NullBooleanField(null=True, blank=True, verbose_name="Abgeschloßen")

    def __str__(self):
        return f"{self.task} - {self.user}"