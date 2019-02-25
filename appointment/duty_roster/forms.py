from django import forms

from appointment.models import DutyRoster


class DutyRosterForm(forms.ModelForm):
    class Meta:
        model = DutyRoster
        fields = ("file", )
