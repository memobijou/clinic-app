from django.urls import path, include
from rest_framework import routers

from appointment.duty_roster.datatables import DutyRosterDatatables
from appointment.duty_roster.views import DutyRosterView
from appointment.serializers import AppointmentViewSet
from appointment.views import AppointmentView, InfoboxView, ConferenceView, InfoboxUpdateView, ConferenceUpdateView
from appointment.duty_roster.serializers import DutyRosterViewSet

# Routers provide an easy way of automatically determining the URL conf.
appointment_router = routers.DefaultRouter()
appointment_router.register(r'', AppointmentViewSet)
duty_roster_router = routers.DefaultRouter()
duty_roster_router.register(r'api', DutyRosterViewSet)


urlpatterns = [
    path(r'api/', include(appointment_router.urls)),
    path(r'duty-roster/', include(duty_roster_router.urls)),
    path(r'', AppointmentView.as_view(), name="planning"),
    path(r'infobox/new', InfoboxView.as_view(), name="new_infobox"),
    path(r'conference/new', ConferenceView.as_view(), name="new_conference"),
    path(r'infobox/<int:pk>/edit', InfoboxUpdateView.as_view(), name="edit_infobox"),
    path(r'conference/<int:pk>/edit', ConferenceUpdateView.as_view(), name="edit_conference"),
    path(r'duty-roster/datatables', DutyRosterDatatables.as_view(), name="duty_roster_datatables"),
    path(r'duty-roster/list', DutyRosterView.as_view(), name="duty_roster_list"),

]
