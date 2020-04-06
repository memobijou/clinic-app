import datetime
from django.db.models import F, Q
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from appointment.models import Appointment
from appointment.serializers import AppointmentSerializer, CalendarAppointmentSerializer
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

    def get_serializer_class(self):
        if self.action == "calendar":
            self.serializer_class = CalendarAppointmentSerializer
        return self.serializer_class

    def get_queryset(self):
        self.queryset = super().get_queryset()

        if self.action == "calendar":
            return Appointment.objects.all()

        self.queryset = self.filter()

        today = datetime.datetime.now()

        self.queryset = self.queryset.exclude(Q(end_date__month=today.month, end_date__day__lt=today.day)
                                              | Q(end_date__month__lt=today.month)
                                              | Q(end_date__year__lt=today.year,))

        if self.kwargs.get("user_id"):
            user = get_object_or_404(User, pk=self.kwargs.get("user_id"))
            user.profile.appointment_badges = 0
            user.profile.save()
        return self.queryset

    def filter(self):
        self.queryset = self.filter_groups_by_user_id()

        start_datetime = self.request.GET.get("start")
        end_datetime = self.request.GET.get("end")

        if start_datetime is not None and end_datetime is not None:
            start_date = datetime.datetime.strptime(start_datetime, "%Y-%m-%d").date()
            end_date = datetime.datetime.strptime(end_datetime, "%Y-%m-%d").date()

            self.queryset = self.queryset.filter(
                start_date__range=(start_date, end_date), end_date__range=(start_date, end_date))
        return self.queryset

    def filter_groups_by_user_id(self):
        user_id = self.kwargs.get("user_id")
        if user_id is not None:
            self.queryset = self.queryset.filter(groups__users__pk=user_id)
        return self.queryset

    # @method_decorator(cache_page(60*60*2))
    @action(detail=False, name="calendar")
    def calendar(self, request):
        # self.queryset = self.filter()
        self.queryset = Appointment.objects.all()

        start_datetime = self.request.GET.get("start")
        end_datetime = self.request.GET.get("end")

        if start_datetime is not None and end_datetime is not None:
            start_date = datetime.datetime.strptime(start_datetime, "%Y-%m-%d").date()
            end_date = datetime.datetime.strptime(end_datetime, "%Y-%m-%d").date()

            self.queryset = self.queryset.filter(
                start_date__range=(start_date, end_date), end_date__range=(start_date, end_date))

            # self.queryset = self.queryset.filter(
            #     Q(start_date__day__gte=start_date.day, start_date__month__gte=start_date.month,
            #       start_date__year__gte=start_date.year) |
            #     Q(end_date__day__lte=end_date.day, end_date__month__lte=end_date.month,
            #       end_date__year__lte=end_date.year)
            # )

        self.pagination_class = None
        serializer = self.get_serializer(self.queryset, many=True)
        return Response(serializer.data)
