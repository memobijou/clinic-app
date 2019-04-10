from django.db import models
from django.urls import reverse_lazy
# Create your models here.


class PhoneBook(models.Model):
    title = models.CharField(null=True, blank=True, max_length=200, verbose_name="Bezeichnung")
    phone_number = models.CharField(null=True, blank=True, max_length=200, verbose_name="Rufnummer")

    @staticmethod
    def get_absolute_url():
        return reverse_lazy("phonebook:list")
