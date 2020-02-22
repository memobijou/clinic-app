from django.db import transaction
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import GenericViewSet
from django.shortcuts import get_object_or_404
from poll.models import Poll, UserOption
from poll.serializers import PollSerializer


class PollViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = Poll.objects.all()
    serializer_class = PollSerializer
    pagination_class = PageNumberPagination
    lookup_field = "id"

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["user_id"] = self.kwargs.get("user_id")
        return context

    def get_queryset(self):
        # if self.kwargs.get("user_id"):
            # self.queryset = self.queryset.filter(users__id=self.kwargs.get("user_id")).distinct()
        return self.queryset

    @transaction.atomic
    @action(detail=True, methods=['PATCH'])
    def select(self, request, user_id=None, id=None):
        print(f"hey: {user_id} - {id}")
        print(f"asfdsaf: {request.data.get('option')}")
        option_id = request.data.get('option')

        user_option = UserOption.objects.filter(user_id=user_id, option_id=option_id).first()

        if user_option:
            user_option.selected = True
            user_option.save()
        else:
            user_option = UserOption(user_id=user_id, option_id=option_id, selected=True)
            user_option.save()

        return Response()

        # serializer = self.serializer_class(instance=instance, data=data)
        # if serializer.is_valid():
        #     instance = serializer.save()
        #     if instance.score == instance.accomplishment.full_score:
        #         instance.completed = True
        #     instance.save()
        #     return Response(serializer.data)
        # else:
        #     return Response(serializer.errors,
        #                     status=status.HTTP_400_BAD_REQUEST)
