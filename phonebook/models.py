from django.db import models
from django.urls import reverse_lazy
# Create your models here.


class PhoneBook(models.Model):
    last_name = models.CharField(null=True, blank=True, max_length=200, verbose_name="Name")
    first_name = models.CharField(null=True, blank=True, max_length=200, verbose_name="Vorname")
    title = models.CharField(null=True, blank=True, max_length=200, verbose_name="Bezeichnung")
    phone_number = models.CharField(null=True, blank=True, max_length=200, verbose_name="Rufnummer")
    mobile_number = models.CharField(null=True, blank=True, max_length=200, verbose_name="Handynummer")

    class Meta:
        ordering = ("last_name", "first_name", "title", )

    @staticmethod
    def get_absolute_url():
        return reverse_lazy("phonebook:list")
