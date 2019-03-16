from django import forms

from filestorage.models import FileDirectory


class DirectoryFormBase(forms.ModelForm):
    class Meta:
        model = FileDirectory
        fields = ("name", )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fields["name"].widget.attrs["class"] = "form-control"
        self.fields["name"].widget.attrs["placeholder"] = "Verzeichnis Bezeichnung"


class FileDirectoryForm(DirectoryFormBase):
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.type = "filestorage"
        instance.save()
        return instance


class DownloadForm(DirectoryFormBase):
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.type = "download"
        instance.save()
        return instance
