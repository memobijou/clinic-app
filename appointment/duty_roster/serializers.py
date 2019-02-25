from django.db.models import Q
from rest_framework import serializers, viewsets
# Serializers define the API representation.
from rest_framework.pagination import LimitOffsetPagination

from appointment.duty_roster.utils import get_first_date_of_week_dates, get_week_dates
from appointment.models import DutyRoster
from datetime import datetime, timedelta


class DutyRosterSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DutyRoster
        fields = ('pk','calendar_week_date', "file", "calendar_week",)

    def validate(self, data):
        today = datetime.now()
        print(f"yes: {today}")
        week_dates = get_week_dates(today)
        query_condition = Q()
        for date in week_dates:
            query_condition |= Q(
                Q(calendar_week_date__day=date.day,
                  calendar_week_date__month=date.month,
                  calendar_week_date__year=date.year)
            )
        print(query_condition)
        duty_rosters = DutyRoster.objects.filter(query_condition)

        if duty_rosters.count() > 0:
            duty_rosters.delete()
        data["calendar_week_date"] = get_first_date_of_week_dates(week_dates)
        return data


# ViewSets define the view behavior.
class DutyRosterViewSet(viewsets.ModelViewSet):
    queryset = DutyRoster.objects.all()
    serializer_class = DutyRosterSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return super().get_queryset()
