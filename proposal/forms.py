from django import forms

from proposal.models import Type


class TypeForm(forms.ModelForm):
    class Meta:
        model = Type
        fields = ("title",)
