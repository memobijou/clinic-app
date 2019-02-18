from django.contrib.auth.models import User
from django.db import models

# Create your models here.
class Task(models.Model):
    name = models.CharField(null=True, blank=False, max_length=200)
    users = models.ManyToManyField(to=User, blank=True, through="taskmanagement.UserTask")


class UserTask(models.Model):
    task = models.ForeignKey("taskmanagement.Task", null=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
