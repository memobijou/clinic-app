import datetime
from django.db.models import F, Q
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from appointment.models import Appointment
from appointment.serializers import AppointmentSerializer
from django.db.models.functions import Concat
from django.db.models import Value, CharField
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404


class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all().order_by("start_date", "end_date")
    serializer_class = AppointmentSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        self.queryset = super().get_queryset()
        today = datetime.datetime.now()
        self.queryset = self.queryset.exclude(
            Q(Q(end_date__year__lt=today.year) | Q(end_date__month__lt=today.month) | Q(end_date__day__lt=today.day)))

        self.filter_by_infobox_or_conference()
        self.filter_by_group_name()
        self.filter_by_group_pks()
        self.filter_groups_by_user_id()

        is_info = self.request.GET.get("is_infobox")
        is_conference = self.request.GET.get("is_conference")

        if is_info == "true":
            self.queryset = self.queryset.filter(is_infobox=True)
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

        if self.kwargs.get("user_id"):
            user = get_object_or_404(User, pk=self.kwargs.get("user_id"))
            user.profile.appointment_badges = 0
            user.profile.save()
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
