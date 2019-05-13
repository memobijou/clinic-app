from django.db.models import F
from rest_framework import serializers, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from account.group.serializers import GroupSerializer
from appointment.models import Appointment
import datetime


# Serializers define the API representation.
class AppointmentSerializer(serializers.HyperlinkedModelSerializer):
    groups = GroupSerializer(many=True)
    promoter = serializers.StringRelatedField()
    start = serializers.SerializerMethodField()
    end = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()

    def get_start(self, instance):
        return instance.start_date

    def get_end(self, instance):
        return instance.end_date

    def get_title(self, instance):
        return instance.topic

    class Meta:
        model = Appointment
        fields = ('pk', 'topic', 'description', 'start_date', 'end_date', "place", "promoter", "is_infobox",
                  "is_conference", "groups", "title", "start", "end",)


# ViewSets define the view behavior.
class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all().order_by("start_date", "end_date")
    serializer_class = AppointmentSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        self.queryset = super().get_queryset()
        self.filter_by_infobox_or_conference()
        self.filter_by_group_name()
        self.filter_by_group_pks()
        self.filter_groups_by_user_id()

        is_info = self.request.GET.get("is_infobox")
        is_conference = self.request.GET.get("is_conference")

        if is_info == "true":
            self.queryset = self.queryset.filter(is_infobox=True)
            from django.db.models.functions import Concat
            from django.db.models import Value, CharField
            self.queryset = self.queryset.annotate(
                promoter_name=Concat(F("promoter__first_name"), Value(' '), F("promoter__last_name"),
                                     output_field=CharField()))
        if is_conference == "true":
            self.queryset = self.queryset.filter(is_conference=True)

        start_datetime = self.request.GET.get("start")
        end_datetime = self.request.GET.get("end")

        if start_datetime is not None and end_datetime is not None:
            start_date = datetime.datetime.strptime(start_datetime, "%Y-%m-%d").date()
            end_date = datetime.datetime.strptime(end_datetime, "%Y-%m-%d").date()

            self.queryset = self.queryset.filter(
                start_date__range=(start_date, end_date), end_date__range=(start_date, end_date))
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
        self.pagination_class = None
        return super().list(request)
