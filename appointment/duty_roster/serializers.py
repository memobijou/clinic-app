from rest_framework import serializers, viewsets
from rest_framework.pagination import PageNumberPagination
from appointment.models import DutyRoster
from datetime import datetime
from django.utils.translation import ugettext as _
from account.models import Profile
from uniklinik.utils import send_push_notifications
from django.db.models import F
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404


class DutyRosterSerializer(serializers.HyperlinkedModelSerializer):
    month = serializers.SerializerMethodField()
    year = serializers.SerializerMethodField()
    month_input = serializers.CharField(write_only=True, label="Monat")
    year_input = serializers.CharField(write_only=True, label="Jahr")

    def get_month(self, instance):
        if instance.calendar_week_date:
            return _(str(instance.calendar_week_date.strftime('%B')))

    def get_year(self, instance):
        if instance.calendar_week_date:
            return _(str(instance.calendar_week_date.strftime('%Y')))

    class Meta:
        model = DutyRoster
        fields = ('pk', 'calendar_week_date', "file", "calendar_week", "month", "year", "month_input", "year_input", )

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

    def create(self, validated_data):
        print(f"come one mannnnn  {validated_data}")

        def update_badge_method(push_user_ids):
            Profile.objects.filter(user_id__in=push_user_ids).update(
                duty_roster_badges=F("duty_roster_badges") + 1)

        month = validated_data.get('calendar_week_date').month

        if len(str(month)) == 1:
            month = "0" + str(month)

        message = f"{month}.{validated_data.get('calendar_week_date').year}"

        print(message)

        create_response = super().create(validated_data)
        send_push_notifications(User.objects.all(), f"Neuer Dienstplan verfügbar", message, "duty-roster",
                                update_badge_method)
        return create_response

# ViewSets define the view behavior.
class DutyRosterViewSet(viewsets.ModelViewSet):
    queryset = DutyRoster.objects.all()
    serializer_class = DutyRosterSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        if self.kwargs.get("user_id"):
            user = get_object_or_404(User, pk=self.kwargs.get("user_id"))
            profile = user.profile
            profile.duty_roster_badges = 0
            profile.save()
        return super().get_queryset()
