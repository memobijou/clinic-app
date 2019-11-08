from django.views.generic import TemplateView
from django.urls import path


urlpatterns = [
    path("chat", TemplateView.as_view(template_name="messaging/chat.html"))
]
