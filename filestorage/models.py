from django.db import models
from decimal import Decimal


# Create your models here.
class FileDirectory(models.Model):
    name = models.CharField(max_length=200, null=True, verbose_name="Ordner")
    type = models.CharField(choices=(("download", "download"), ("filestorage", "filestorage")), max_length=200,
                            default="filestorage")
    announcement = models.NullBooleanField(null=True, blank=True, verbose_name="Ankündigung")

    parent = models.ForeignKey("filestorage.FileDirectory", null=True, blank=True, related_name="child_directories",
                               on_delete=models.SET_NULL)

    class Meta:
        ordering = ("pk", )


class File(models.Model):
    class Meta:
        ordering = ("-pk", )

    file = models.FileField(null=True, verbose_name="Datei")
    parent_directory = models.ForeignKey("filestorage.FileDirectory", null=True, verbose_name="Ordnerstruktur",
                                         on_delete=models.SET_NULL, related_name="files")
    version = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Version", default=1.0)

    @property
    def version_with_point(self):
        if self.version:
            rounded_version = round(Decimal(self.version), 2)
            return str(rounded_version).replace(",", ".")
