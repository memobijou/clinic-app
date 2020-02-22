from django.urls import path, include
from rest_framework import routers

from poll.viewsets import PollViewSet

router = routers.DefaultRouter()
router.register(r'polls', PollViewSet, basename="poll")


urlpatterns = [
    path(r'users/<int:user_id>/', include(router.urls)),
]
