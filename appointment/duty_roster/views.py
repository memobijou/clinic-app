from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View
from appointment.duty_roster.forms import DutyRosterForm
from datetime import datetime
from appointment.models import DutyRoster
from django.http.response import HttpResponseRedirect
from django.urls import reverse_lazy


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
                "current_duty_roster": self.get_current_duty_roster(), "current_datetime": datetime.now()
        }

    def get_current_duty_roster(self):
        today = datetime.now()
        duty_roster = DutyRoster.objects.filter(
            calendar_week_date__month=today.month,
            calendar_week_date__year=today.year
        )
        if duty_roster.count() > 0:
            return duty_roster.first()


class DutyRosterDeleteView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        items = request.POST.getlist("item")
        print(f"abc abc: {items}")
        DutyRoster.objects.filter(pk__in=items).delete()
        return HttpResponseRedirect(reverse_lazy("appointment:duty_roster_list"))
