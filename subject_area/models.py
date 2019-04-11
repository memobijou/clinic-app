from django.db import models
from django.urls import reverse_lazy
# Create your models here.


class SubjectArea(models.Model):
    title = models.CharField(max_length=200, verbose_name="Bezeichnung")

    @staticmethod
    def get_absolute_url():
        return reverse_lazy("subject_area:list")

    def __str__(self):
        return self.title
