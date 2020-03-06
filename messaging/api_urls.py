from rest_framework import routers
from messaging.viewsets import TextMessageViewset, ReceiverTextMessageViewSet, GroupTextMessageViewSet
from django.urls import path, include

router = routers.DefaultRouter()
router.register(r'', TextMessageViewset, basename="messaging")
receiver_router = routers.DefaultRouter()
receiver_router.register(r"", ReceiverTextMessageViewSet, basename="receiver_messaging")
group_messages_router = routers.DefaultRouter()
group_messages_router.register(r"", GroupTextMessageViewSet, basename="group_messaging")

urlpatterns = [
    path(r'messaging/<int:receiver>/<int:sender>/', include(router.urls)),
    path(r'messaging/<int:receiver>/', include(receiver_router.urls)),
    path(r'messaging/groups/<int:group>/messages', include(group_messages_router.urls)),
]
