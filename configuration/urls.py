from configuration.views import configuration_view
from django.urls import path


urlpatterns = [
    path(r'', configuration_view, name="config"),

]
