from django.views.generic import TemplateView
from django.urls import path
from messaging.views import alarm

urlpatterns = [
    path("chat", TemplateView.as_view(template_name="messaging/chat.html")),
    path("chat2", TemplateView.as_view(template_name="messaging/chat2.html")),
    path("alarm", alarm)

]
