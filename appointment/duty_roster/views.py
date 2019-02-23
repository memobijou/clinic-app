from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View


class DutyRosterView(LoginRequiredMixin, View):
    template_name = "appointment/duty_roster/duty_roster.html"

    def __init__(self):
        super().__init__()

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context())

    def get_context(self):
        return {}
