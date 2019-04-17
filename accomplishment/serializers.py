from django.db import transaction
from django.db.models import F, Q
from rest_framework import serializers, viewsets, status
from rest_framework.pagination import PageNumberPagination
from accomplishment.models import Accomplishment, UserAccomplishment
from account.serializers import UserSerializer
from rest_framework.decorators import action
from rest_framework.response import Response


class AccomplishmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Accomplishment
        fields = ("pk", "name", "full_score", )


class UserAccomplishmentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    accomplishment = AccomplishmentSerializer(read_only=True)
    completed = serializers.NullBooleanField(read_only=True)

    class Meta:
        model = UserAccomplishment
        fields = ('score', 'user', "accomplishment", "completed", )

    def validate_score(self, value):
        if value > self.instance.accomplishment.full_score:
            raise serializers.ValidationError(
                "Die Gesamtpunktezahl wurde erreicht und kann nicht mehr weiter erhöht werden.")
        elif value < 0:
            raise serializers.ValidationError("Die Punktezahl kann nicht kleiner als 0 sein.")
        return value


class AccomplishmentViewSet(viewsets.ModelViewSet):
    queryset = UserAccomplishment.objects.prefetch_related(
        "accomplishment__users").select_related("accomplishment").exclude(
        ~Q(user__in=F("accomplishment__subject_areas__profiles__user"))).distinct()
    serializer_class = UserAccomplishmentSerializer
    pagination_class = PageNumberPagination
    lookup_field = "accomplishment_id"

    def get_queryset(self):
        user_id = self.kwargs.get("user_id")

        if user_id:
            self.queryset = self.queryset.filter(user__pk=user_id).distinct()

        return self.queryset

    @transaction.atomic
    @action(detail=True, methods=['PUT'])
    def incrementation(self, request, user_id=None, accomplishment_id=None):
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
