from django.urls import path, include
from rest_framework import routers
from appointment.viewsets import AppointmentViewSet
from appointment.duty_roster.serializers import DutyRosterViewSet

appointment_router = routers.DefaultRouter()
appointment_router.register(r'appointments', AppointmentViewSet, basename="appointment")

duty_roster_router = routers.DefaultRouter()
duty_roster_router.register(r'api', DutyRosterViewSet, basename="duty_roster")


urlpatterns = [
    path(r'users/<int:user_id>/', include(appointment_router.urls)),
]
