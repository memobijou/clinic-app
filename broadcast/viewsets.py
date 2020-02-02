from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin
from django.db.transaction import atomic
from broadcast.models import Broadcast, Like, Comment, Attachement
from broadcast.serializers import BroadcastSerializer, LikeSerializer, CommentSerializer


class BroadcastViewSet(ListModelMixin, RetrieveModelMixin, CreateModelMixin, GenericViewSet):
    serializer_class = BroadcastSerializer
    queryset = Broadcast.objects.all()

    @atomic
    def perform_create(self, serializer):
        print(self.request.FILES)
        instance = serializer.save()
        for f in self.request.FILES.getlist("attachements"):
            a = Attachement(broadcast_id=self.kwargs.get("broadcast_id"))
            a.file.save(f.name, f.file, True)
            instance.attachement_set.add(a)
        instance.save()


class LikeViewSet(ListModelMixin, CreateModelMixin, GenericViewSet):
    serializer_class = LikeSerializer
    queryset = Like.objects.all()

    def get_queryset(self):
        return self.queryset.filter(broadcast_id=self.kwargs.get("broadcast_id"))

    @atomic
    def perform_create(self, serializer):
        instance = serializer.save()
        instance.broadcast_id = self.kwargs.get("broadcast_id")
        instance.save()


class CommentViewSet(ListModelMixin, RetrieveModelMixin,  CreateModelMixin,  GenericViewSet):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()

    def get_queryset(self):
        print(self.kwargs.get("broadcast_id"))
        return Broadcast.objects.get(pk=self.kwargs.get("broadcast_id")).comment_set.all()

    @atomic
    def perform_create(self, serializer):
        instance = serializer.save()
        instance.broadcast_id = self.kwargs.get("broadcast_id")
        instance.save()
