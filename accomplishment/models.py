from django.contrib.auth.models import User
from django.db import models

# Create your models here.


class Accomplishment(models.Model):
    name = models.CharField(max_length=200, null=True, blank=False, verbose_name="Bezeichnung")
    full_score = models.IntegerField(null=True, blank=False, verbose_name="Gesamtpunktezahl")
    groups = models.ManyToManyField("account.Group", related_name="accomplishments", verbose_name="Gruppen")
    users = models.ManyToManyField(User, blank=True, through="accomplishment.UserAccomplishment",
                                   related_name="accomplishments", verbose_name="Benutzer")


class UserAccomplishment(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL,
                             related_name="user_accomplishments")
    accomplishment = models.ForeignKey(Accomplishment, null=True, blank=True, on_delete=models.SET_NULL,
                                       related_name="user_accomplishments")
    score = models.IntegerField(null=True, blank=True)
