from rest_framework import serializers, viewsets, status
from rest_framework.pagination import LimitOffsetPagination
from accomplishment.models import Accomplishment, UserAccomplishment
from account.serializers import UserSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404


class AccomplishmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Accomplishment
        fields = ("pk", "name", "full_score", )


class UserAccomplishmentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    accomplishment = AccomplishmentSerializer(read_only=True)

    class Meta:
        model = UserAccomplishment
        fields = ('score', 'user', "accomplishment", )

    def validate_score(self, value):
        if value > self.instance.accomplishment.full_score:
            raise serializers.ValidationError(
                "Die Gesamtpunktezahl wurde erreicht und kann nicht mehr weiter erhöht werden.")
        elif value < 0:
            raise serializers.ValidationError("Die Punktezahl kann nicht kleiner als 0 sein.")
        return value


class AccomplishmentViewSet(viewsets.ModelViewSet):
    queryset = UserAccomplishment.objects.all()
    serializer_class = UserAccomplishmentSerializer
    pagination_class = LimitOffsetPagination
    lookup_field = "accomplishment_id"

    def get_queryset(self):
        user_id = self.kwargs.get("user_id")
        group_id = self.request.GET.get("group_id")

        if user_id:
            self.queryset = self.queryset.filter(user__pk=user_id).distinct()

        if group_id:
            self.queryset = self.queryset.filter(groups__pk=group_id).distinct()

        return self.queryset

    @action(detail=True, methods=['PUT'])
    def incrementation(self, request, user_id=None, accomplishment_id=None):
        instance = self.get_object()
        data = {**request.data, "score": instance.score + 5}
        serializer = self.serializer_class(instance=instance, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['PUT'])
    def decrementation(self, request, user_id=None, accomplishment_id=None):
        instance = self.get_object()
        data = {**request.data, "score": instance.score - 5}
        serializer = self.serializer_class(instance=instance, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
