from django.db import models


# Create your models here.
class FileDirectory(models.Model):
    name = models.CharField(max_length=200, null=True, verbose_name="Ordner")


class File(models.Model):
    file = models.FileField(null=True, verbose_name="Datei")
    parent_directory = models.ForeignKey("filestorage.FileDirectory", null=True, verbose_name="Ordnerstruktur",
                                         on_delete=models.SET_NULL)

