from rest_framework import routers
from messaging.viewsets import TextMessageViewset, ReceiverTextMessageViewSet
from django.urls import path, include

router = routers.DefaultRouter()
router.register(r'', TextMessageViewset, basename="messaging")
receiver_router = routers.DefaultRouter()
receiver_router.register(r"", ReceiverTextMessageViewSet, basename="receiver_messaging")

urlpatterns = [
    path(r'messaging/<int:receiver>/<int:sender>/', include(router.urls)),
    path(r'messaging/<int:receiver>/', include(receiver_router.urls)),
]
