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
    groups = models.ManyToManyField("account.Group", related_name="appointments", verbose_name="Gruppen")

class DutyRoster(models.Model):
    calendar_week_date = models.DateTimeField(null=True, verbose_name="Datum Dienstplan")
    file = models.FileField(null=True, verbose_name="Dienstplan")

    class Meta:
        ordering = ("-calendar_week_date", )

    @property
    def calendar_week(self):
        if self.calendar_week_date is not None:
            return self.calendar_week_date.isocalendar()[1]
