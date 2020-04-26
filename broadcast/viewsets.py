from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin, DestroyModelMixin
from django.db.transaction import atomic
from broadcast.models import Broadcast, Like, Comment, Attachement
from broadcast.serializers import BroadcastSerializer, LikeSerializer, CommentSerializer
from uniklinik.utils import send_push_notifications
from django.contrib.auth.models import User
from account.models import Profile
from django.db.models import F
from django.shortcuts import get_object_or_404


class BroadcastViewSet(ListModelMixin, RetrieveModelMixin, CreateModelMixin, DestroyModelMixin, GenericViewSet):
    serializer_class = BroadcastSerializer
    queryset = Broadcast.objects.all()

    def get_serializer_context(self):
        context = super().get_serializer_context()

        user_id = self.request.query_params.get("user_id")

        if user_id:
            user = get_object_or_404(User, pk=user_id)
            profile = user.profile
            profile.broadcast_badges = 0
            profile.save()
        return context

    @atomic
    def perform_create(self, serializer):
        print(self.request.FILES)
        instance = serializer.save()
        for f in self.request.FILES.getlist("attachements"):
            a = Attachement(broadcast_id=self.kwargs.get("broadcast_id"))
            a.file.save(f.name, f.file, True)
            instance.attachement_set.add(a)
        instance.save()

        def update_badge_method(push_user_ids):
            Profile.objects.filter(user_id__in=push_user_ids).update(broadcast_badges=F("broadcast_badges") + 1)

        send_push_notifications(
            User.objects.exclude(id=instance.sender_id), f'Neue Nachricht von {instance.sender}',
            instance.text, "broadcast", update_badge_method
        )

    @atomic
    def perform_destroy(self, instance):
        instance.comment_set.all().delete()
        instance.like_set.all().delete()
        instance.delete()


class LikeViewSet(CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, ListModelMixin, GenericViewSet):
    serializer_class = LikeSerializer
    queryset = Like.objects.all()

    def get_queryset(self):
        return self.queryset.filter(broadcast_id=self.kwargs.get("broadcast_id"))

    def get_object(self):
        print(f"??? {self.kwargs.get('pk')}")
        return Like.objects.get(pk=self.kwargs.get("pk"))

    @atomic
    def perform_create(self, serializer):
        instance = serializer.save()
        instance.broadcast_id = self.kwargs.get("broadcast_id")
        instance.save()

        def update_badge_method(push_user_ids):
            Profile.objects.filter(user_id__in=push_user_ids).update(broadcast_badges=F("broadcast_badges") + 1)

        send_push_notifications(
            User.objects.filter(id=instance.broadcast.sender_id), f'{instance.user} gefällt dein Beitrag!',
            f"{instance.broadcast.text}", "broadcast-like", update_badge_method
        )


class CommentViewSet(ListModelMixin, RetrieveModelMixin,  CreateModelMixin,  GenericViewSet, DestroyModelMixin):
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

        def update_badge_method(push_user_ids):
            Profile.objects.filter(user_id__in=push_user_ids).update(broadcast_badges=F("broadcast_badges") + 1)

        send_push_notifications(
            User.objects.filter(id=instance.broadcast.sender_id), f'{instance.sender} hat deinen Beitrag kommentiert',
            instance.text, "broadcast-comment", update_badge_method
        )
