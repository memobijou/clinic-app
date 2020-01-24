from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.mixins import ListModelMixin, CreateModelMixin
from django.db.transaction import atomic
from broadcast.models import Broadcast, Like
from broadcast.serializers import BroadcastSerializer, LikeSerializer


class BroadcastViewSet(ListModelMixin, CreateModelMixin,  GenericViewSet):
    serializer_class = BroadcastSerializer
    queryset = Broadcast.objects.all()


class LikeViewSet(ListModelMixin, CreateModelMixin,  GenericViewSet):
    serializer_class = LikeSerializer
    queryset = Like.objects.all()

    def get_queryset(self):
        return self.queryset.filter(broadcast_id=self.kwargs.get("broadcast_id"))

    @atomic
    def perform_create(self, serializer):
        instance = serializer.save()
        instance.broadcast_id = self.kwargs.get("broadcast_id")
        instance.save()
