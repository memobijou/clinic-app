from django.db import models


# Create your models here.
class FileDirectory(models.Model):
    name = models.CharField(max_length=200, null=True, verbose_name="Ordner")
    type = models.CharField(choices=(("download", "download"), ("filestorage", "filestorage")), max_length=200,
                            default="filestorage")


class File(models.Model):
    file = models.FileField(null=True, verbose_name="Datei")
    parent_directory = models.ForeignKey("filestorage.FileDirectory", null=True, verbose_name="Ordnerstruktur",
                                         on_delete=models.SET_NULL, related_name="files")
    version = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Version", default=1.0)
