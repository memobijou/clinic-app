from rest_framework import routers
from messaging.viewsets import TextMessageViewset
from django.urls import path, include

router = routers.DefaultRouter()
router.register(r'', TextMessageViewset, basename="messaging")


urlpatterns = [
    path(r'messaging/<int:receiver>/<int:sender>/', include(router.urls)),
    path(r'messaging/<int:receiver>/', include(router.urls)),
]
