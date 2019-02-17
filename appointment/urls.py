from django.urls import path, include
from rest_framework import routers
from appointment.serializers import AppointmentViewSet
from appointment.views import AppointmentView, InfoboxView, ConferenceView, InfoboxUpdateView, ConferenceUpdateView

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
