import datetime
from django.db.models import F, Q
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from appointment.models import Appointment
from appointment.serializers import AppointmentSerializer
from django.db.models.functions import Concat
from django.db.models import Value, CharField
from account.models import User
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from django.contrib.auth.models import User


class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all().order_by("start_date", "end_date")
    serializer_class = AppointmentSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        self.queryset = super().get_queryset()
        self.queryset = self.filter()

        today = datetime.datetime.now()

        self.queryset = self.queryset.exclude(Q(end_date__month=today.month, end_date__day__lt=today.day)
                                              | Q(end_date__month__lt=today.month)
                                              | Q(end_date__year__lt=today.year,))

        self.queryset = self.queryset.exclude(is_infobox=True)

        if self.kwargs.get("user_id"):
            user = get_object_or_404(User, pk=self.kwargs.get("user_id"))
            user.profile.appointment_badges = 0
            user.profile.save()
        return self.queryset

    def filter(self):
        self.filter_by_group_name()
        self.filter_by_group_pks()
        self.filter_groups_by_user_id()

        is_conference = self.request.GET.get("is_conference")
        is_infobox = self.request.GET.get("is_infobox")  # backwards compatibility

        if is_infobox == "true":  # backwards compatibility
            return Appointment.objects.none()

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

    @action(detail=False, name="calendar")
    def calendar(self, request):
        self.queryset = Appointment.objects.all()
        self.queryset = self.filter()
        self.pagination_class = None
        serializer = self.get_serializer(self.queryset, many=True)
        return Response(serializer.data)
