from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View
from appointment.duty_roster.forms import DutyRosterForm
from datetime import datetime

from appointment.duty_roster.utils import get_week_dates, get_first_date_of_week_dates
from appointment.models import DutyRoster


class DutyRosterView(LoginRequiredMixin, View):
    template_name = "appointment/duty_roster/duty_roster.html"
    form = DutyRosterForm()

    def __init__(self):
        super().__init__()

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context())

    def get_context(self):
        return {
                "form": self.form, "calendar_week": datetime.now().isocalendar()[1],
                "current_duty_roster": self.get_current_duty_roster()
        }

    def get_current_duty_roster(self):
        today = datetime.now()
        week_dates = get_week_dates(today)
        first_week_date = get_first_date_of_week_dates(week_dates)
        duty_roster = DutyRoster.objects.filter(
            calendar_week_date__day=first_week_date.day, calendar_week_date__month=first_week_date.month,
            calendar_week_date__year=first_week_date.year
        )
        if duty_roster.count() > 0:
            return duty_roster.first()

