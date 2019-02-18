from django.db import models
from django.contrib.auth.models import User
# Create your models here.


def get_name(self):
    return f"{self.first_name or ''} {self.last_name or ''}"


User.add_to_class("__str__", get_name)


class Group(models.Model):
    name = models.CharField(null=True, blank=False, max_length=200)
    users = models.ManyToManyField(User, blank=True, related_name="groups_list")
    tasks = models.ManyToManyField("taskmanagement.Task", blank=True, related_name="groups_list")
