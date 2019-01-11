from django import forms

from filestorage.models import FileDirectory


class DirectoryForm(forms.ModelForm):
    class Meta:
        model = FileDirectory
        fields = ("name", )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fields["name"].widget.attrs["class"] = "form-control"
        self.fields["name"].widget.attrs["placeholder"] = "Verzeichnis Bezeichnung"
