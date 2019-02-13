from django.contrib.auth.models import User
from django.db.models import F
from django.urls import path, include
from rest_framework import routers, serializers, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from appointment.models import Appointment
from appointment.views import AppointmentView, InfoboxView, ConferenceView, InfoboxUpdateView, ConferenceUpdateView
import datetime


# Serializers define the API representation.
class AppointmentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Appointment
        fields = ('pk', 'topic', 'description', 'start_date', 'end_date', "place", "promoter", "is_infobox",
                  "is_conference")
    promoter = serializers.StringRelatedField()


# ViewSets define the view behavior.
class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.GET.get("is_infobox") == "true":
            queryset = queryset.filter(is_infobox=True)
        elif self.request.GET.get("is_conference") == "true":
            queryset = queryset.filter(is_conference=True)
        return queryset

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


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'', AppointmentViewSet)


urlpatterns = [
    path(r'api/', include(router.urls)),
    path(r'', AppointmentView.as_view(), name="planning"),
    path(r'infobox/new', InfoboxView.as_view(), name="new_infobox"),
    path(r'conference/new', ConferenceView.as_view(), name="new_conference"),
    path(r'infobox/<int:pk>/edit', InfoboxUpdateView.as_view(), name="edit_infobox"),
    path(r'conference/<int:pk>/edit', ConferenceUpdateView.as_view(), name="edit_conference"),

]
