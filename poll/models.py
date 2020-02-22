from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Poll(models.Model):
    title = models.CharField(max_length=200, null=True, blank=True, verbose_name="Bezeichnung")
    description = models.TextField(null=True, blank=True, verbose_name="Beschreibung")
    created_datetime = models.DateTimeField(null=True, auto_now=True)
    open = models.BooleanField(default=False, verbose_name="Veröffentlichen")


class Option(models.Model):
    class Meta:
        ordering = ("pk",)

    title = models.CharField(max_length=200)
    poll = models.ForeignKey("poll.Poll", null=True, blank=True, verbose_name="Option", on_delete=models.SET_NULL)
    user_options = models.ManyToManyField(User, through='poll.UserOption')


class UserOption(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    option = models.ForeignKey("poll.Option", null=True, blank=True, on_delete=models.SET_NULL)
    selected = models.BooleanField(default=False)
    created_datetime = models.DateTimeField(null=True, auto_now=True)
