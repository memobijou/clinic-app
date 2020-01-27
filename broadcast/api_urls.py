from rest_framework import routers
from broadcast.viewsets import BroadcastViewSet, LikeViewSet, CommentViewSet
from django.urls import path, include

router = routers.DefaultRouter()
router.register(r'', BroadcastViewSet, basename="broadcast")

likes_router = routers.DefaultRouter()
likes_router.register(r'', LikeViewSet, basename="likes")

comments_router = routers.DefaultRouter()
comments_router.register(r'', CommentViewSet, basename="comments")

urlpatterns = [
    path(r'broadcasts/', include(router.urls)),
    path(r'broadcasts/<int:broadcast_id>/likes', include(likes_router.urls)),
    path(r'broadcasts/<int:broadcast_id>/comments', include(comments_router.urls)),
]
