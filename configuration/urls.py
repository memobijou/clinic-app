from configuration.views import configuration_view, logo_view
from django.urls import path


urlpatterns = [
    path(r'', configuration_view, name="config"),
    path(r'logo', logo_view, name="logo"),

]
