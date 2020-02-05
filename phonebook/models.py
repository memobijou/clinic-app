from django.db import models
from django.urls import reverse_lazy
# Create your models here.


class PhoneBook(models.Model):
    last_name = models.CharField(null=True, blank=True, max_length=200, verbose_name="Name")
    first_name = models.CharField(null=True, blank=True, max_length=200, verbose_name="Vorname")
    title = models.CharField(null=True, blank=True, max_length=200, verbose_name="Bezeichnung",
                             help_text='*Um den Kontakt für die Nutzer auszublenden tragen Sie "SPERRE" '
                                       'für die Bezeichnung ein')
    phone_number = models.CharField(null=True, blank=True, max_length=200, verbose_name="Rufnummer")
    mobile_number = models.CharField(null=True, blank=True, max_length=200, verbose_name="Handynummer")
    category = models.ForeignKey("phonebook.Category", null=True, blank=True, on_delete=models.SET_NULL,
                                 verbose_name="Kategorie")

    class Meta:
        ordering = ("last_name", "first_name", "title", )

    @staticmethod
    def get_absolute_url():
        return reverse_lazy("phonebook:list")


class Category(models.Model):
    title = models.CharField(max_length=200, verbose_name="Bezeichnung")

    @staticmethod
    def get_absolute_url():
        return reverse_lazy("phonebook-category:list")

    def __str__(self):
        if self.title:
            return f"{self.title}"

