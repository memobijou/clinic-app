from django.db.models import Q
from rest_framework import serializers, viewsets
from rest_framework.pagination import PageNumberPagination

from appointment.duty_roster.utils import get_first_date_of_week_dates, get_week_dates
from appointment.models import DutyRoster
from datetime import datetime
from django.utils.translation import ugettext as _


class DutyRosterSerializer(serializers.HyperlinkedModelSerializer):
    month = serializers.SerializerMethodField()
    month_input = serializers.CharField(write_only=True, label="Monat")
    year_input = serializers.CharField(write_only=True, label="Jahr")

    def get_month(self, instance):
        if instance.calendar_week_date:
            return _(str(instance.calendar_week_date.strftime('%B')))

    class Meta:
        model = DutyRoster
        fields = ('pk', 'calendar_week_date', "file", "calendar_week", "month", "month_input", "year_input", )

    def validate(self, data):
        print(data)
        month_input = int(data.pop("month_input"))
        year_input = int(data.pop("year_input"))
        date = datetime(day=5, month=month_input, year=year_input)
        duty_rosters = DutyRoster.objects.filter(
            calendar_week_date__month=date.month, calendar_week_date__year=date.year)

        if duty_rosters.count() > 0:
            duty_rosters.delete()
        data["calendar_week_date"] = date
        return data


# ViewSets define the view behavior.
class DutyRosterViewSet(viewsets.ModelViewSet):
    queryset = DutyRoster.objects.all()
    serializer_class = DutyRosterSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        return super().get_queryset()
