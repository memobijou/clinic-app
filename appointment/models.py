from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class Appointment(models.Model):
    start_date = models.DateTimeField(null=True, verbose_name="Startdatum")
    end_date = models.DateTimeField(null=True, verbose_name="Enddatum")
    place = models.CharField(max_length=200, null=True, verbose_name="Treffpunkt")
    promoter = models.ForeignKey(User, null=True, verbose_name="Veranstalter", on_delete=models.SET_NULL)
    is_infobox = models.NullBooleanField(verbose_name="Infobox")
    is_conference = models.NullBooleanField(verbose_name="Konferenz")
    topic = models.CharField(max_length=200, null=True, verbose_name="Thema")
    description = models.TextField(null=True, verbose_name="Beschreibung")


class DutyRoster(models.Model):
    upload_date = models.DateTimeField(null=True, verbose_name="Datum Dienstplan")
    file = models.FileField(null=True, verbose_name="Dienstplan")

    @property
    def calendar_week(self):
        if self.upload_date is not None:
            return self.upload_date.isocalendar()[1]
