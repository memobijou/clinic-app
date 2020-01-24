from rest_framework import routers
from broadcast.viewsets import BroadcastViewSet, LikeViewSet
from django.urls import path, include

router = routers.DefaultRouter()
router.register(r'', BroadcastViewSet, basename="broadcast")

likes_router = routers.DefaultRouter()
likes_router.register(r'', LikeViewSet, basename="likes")

urlpatterns = [
    path(r'broadcasts/', include(router.urls)),
    path(r'broadcasts/<int:broadcast_id>/likes', include(likes_router.urls)),
]
