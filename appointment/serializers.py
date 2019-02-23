from django.db.models import F
from rest_framework import serializers, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from account.group.serializers import GroupSerializer
from appointment.models import Appointment, DutyRoster
import datetime


# Serializers define the API representation.
class AppointmentSerializer(serializers.HyperlinkedModelSerializer):
    groups = GroupSerializer(many=True)

    class Meta:
        model = Appointment
        fields = ('pk', 'topic', 'description', 'start_date', 'end_date', "place", "promoter", "is_infobox",
                  "is_conference", "groups")
    promoter = serializers.StringRelatedField()


# ViewSets define the view behavior.
class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        self.queryset = super().get_queryset()
        self.filter_by_infobox_or_conference()
        self.filter_by_group_name()
        self.filter_by_group_pks()
        self.filter_groups_by_user_id()
        return self.queryset

    def filter_by_group_name(self):
        group_name = self.request.GET.get("group_name")
        print(group_name)
        if group_name is not None:
            self.queryset = self.queryset.filter(groups__name__iexact=group_name)

    def filter_by_group_pks(self):
        group_pks = self.request.GET.getlist("group_pk")
        print(f"hey sammy: {group_pks}")
        if len(group_pks) > 0:
            self.queryset = self.queryset.filter(groups__pk__in=group_pks)

    def filter_groups_by_user_id(self):
        user_id = self.request.GET.get("user_id")
        if user_id is not None:
            self.queryset = self.queryset.filter(groups__users__pk=user_id)

    def filter_by_infobox_or_conference(self):
        if self.request.GET.get("is_infobox") == "true":
            self.queryset = self.queryset.filter(is_infobox=True)
        elif self.request.GET.get("is_conference") == "true":
            self.queryset = self.queryset.filter(is_conference=True)


    @action(detail=False, name="calendar")
    def calendar(self, request):
        print("GOOD")
        print(request.GET.get("start"))
        print(request.GET.get("end"))
        to_filter_start_date = request.GET.get("start")
        to_filter_end_date = request.GET.get("end")
        is_info = request.GET.get("is_infobox")
        is_conference = request.GET.get("is_conference")

        print(f"is_conference : {is_conference} --- is_info : {is_info}")

        data = Appointment.objects.all().values("start_date", "end_date", "description", "pk", "place", "is_infobox",
                                                "is_conference").annotate(
            start=F("start_date"), end=F("end_date"), title=F("topic"))

        if to_filter_start_date is not None and to_filter_end_date is not None:
            to_filter_start_date = datetime.datetime.strptime(to_filter_start_date, "%Y-%m-%d").date()
            to_filter_end_date = datetime.datetime.strptime(to_filter_end_date, "%Y-%m-%d").date()

            data = data.filter(start_date__range=(to_filter_start_date, to_filter_end_date),
                               end_date__range=(to_filter_start_date, to_filter_end_date)
                               )

        if is_info == "true":
            data = data.filter(is_infobox=True)
            from django.db.models.functions import Concat
            from django.db.models import Value, CharField
            data = data.annotate(promoter_name=Concat(F("promoter__first_name"), Value(' '), F("promoter__last_name"),
                                                      output_field=CharField()))
        if is_conference == "true":
            data = data.filter(is_conference=True)

        return Response(data)
