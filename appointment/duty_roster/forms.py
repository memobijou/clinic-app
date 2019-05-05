from django import forms
from appointment.models import DutyRoster
from uniklinik.forms import BootstrapModelFormMixin
from datetime import datetime

year_choices = ((year, year) for year in range(2000, 2100))
months = ("Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September",
          "Oktober", "November", "Dezember")
months_choices = ((i+1, month) for i, month in enumerate(months))


class DutyRosterForm(BootstrapModelFormMixin):
    month = forms.ChoiceField(label="Monat", choices=months_choices, initial=datetime.now().month)
    year = forms.ChoiceField(label="Jahr", choices=year_choices, initial=datetime.now().year)

    class Meta:
        model = DutyRoster
        fields = ("month", "year", )
