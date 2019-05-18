from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Task(models.Model):
    name = models.CharField(null=True, blank=False, max_length=200)
    description = models.TextField(null=True, blank=True, verbose_name="Beschreibung")
    users = models.ManyToManyField(to=User, blank=True, through="taskmanagement.UserTask",
                                   related_name="tasks", verbose_name="Benutzer")

    start_datetime = models.DateTimeField(null=True, verbose_name="Startdatum", blank=True)
    end_datetime = models.DateTimeField(null=True, verbose_name="Enddatum", blank=True)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        ordering = ("-pk", )


class UserTask(models.Model):
    task = models.ForeignKey("taskmanagement.Task", null=True, on_delete=models.CASCADE, related_name="usertasks")
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="usertasks")
    completed = models.NullBooleanField(null=True, blank=True, verbose_name="Abgeschloßen")

    def __str__(self):
        return f"{self.task} - {self.user}"
