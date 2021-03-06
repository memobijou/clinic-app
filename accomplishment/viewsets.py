from django.db import transaction
from django.db.models import Q, F
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from accomplishment.models import UserAccomplishment
from accomplishment.serializers import UserAccomplishmentSerializer
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
User = get_user_model()


class AccomplishmentViewSet(viewsets.ModelViewSet):
    queryset = UserAccomplishment.objects.prefetch_related("accomplishment__users").select_related(
        "accomplishment").annotate(
        divison=F('score') / F('accomplishment__full_score')
    ).annotate(percentage=F('divison') * 100).all().order_by("percentage")
    serializer_class = UserAccomplishmentSerializer
    pagination_class = PageNumberPagination
    lookup_field = "accomplishment_id"

    def get_queryset(self):
        user_id = self.kwargs.get("user_id")
        accomplishment_id = self.kwargs.get("accomplishment_id")

        if accomplishment_id:
            self.queryset = self.queryset.filter(accomplishment__pk=accomplishment_id)
        # exclude stellt sicher das User die nicht mehr zur Fachrichtung gehören ausgeschloßen werden
        self.queryset = self.queryset.filter(user__pk=user_id).exclude(
            ~Q(user__in=F("accomplishment__categories__subject_area__profiles__user"))).distinct()

        if user_id:
            user = get_object_or_404(User, pk=user_id)
            user.profile.accomplishment_badges = 0
            user.profile.save()
        return self.queryset

    @transaction.atomic
    @action(detail=True, methods=['PUT'])
    def incrementation(self, request, user_id=None, accomplishment_id=None):
        print(f"hey: {user_id} - {accomplishment_id}")
        instance = self.get_object()
        data = {**request.data, "score": instance.score + 1}
        serializer = self.serializer_class(instance=instance, data=data)
        if serializer.is_valid():
            instance = serializer.save()
            if instance.score == instance.accomplishment.full_score:
                instance.completed = True
            instance.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    @action(detail=True, methods=['PUT'])
    def decrementation(self, request, user_id=None, accomplishment_id=None):
        instance = self.get_object()
        data = {**request.data, "score": instance.score - 1}
        serializer = self.serializer_class(instance=instance, data=data)
        if serializer.is_valid():
            instance = serializer.save()
            if instance.score != instance.accomplishment.full_score:
                instance.completed = None
            instance.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
