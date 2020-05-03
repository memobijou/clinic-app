from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Proposal(models.Model):
    class Meta:
        ordering = ("-pk",)

    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    start_date = models.DateField(null=True, blank=True, verbose_name="Startdatum")
    end_date = models.DateField(null=True, blank=True, verbose_name="Enddatum")
    confirmed = models.NullBooleanField(verbose_name="Bestätigen")
    type = models.ForeignKey("proposal.Type", null=True, blank=True, verbose_name="Typ", on_delete=models.SET_NULL)


class Type(models.Model):
    title = models.CharField(max_length=200, null=True, blank=True, verbose_name="Bezeichnung")

    def __str__(self):
        if self.title:
            return self.title
        return ""
