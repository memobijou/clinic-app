from abc import ABCMeta, abstractmethod

from django.db.models import Q, Subquery, OuterRef, Count, IntegerField
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from messaging.models import TextMessage
from messaging.serializers import TextMessageSerializer
from rest_framework.mixins import ListModelMixin


class TextMessageViewset(viewsets.GenericViewSet, ListModelMixin):
    serializer_class = TextMessageSerializer
    queryset = TextMessage.objects.all()

    def get_queryset(self):
        self.filter_by_users()
        return self.queryset

    def filter_by_users(self):
        sender_pk = self.kwargs.get("sender")
        receiver_pk = self.kwargs.get("receiver")

        if sender_pk and receiver_pk not in ["", None]:
            self.queryset = self.queryset.filter(
                Q(Q(Q(sender__pk=sender_pk) & Q(receiver__pk=receiver_pk)) |
                  Q(Q(sender__pk=receiver_pk) & Q(receiver__pk=sender_pk))))
        elif receiver_pk not in ["", None]:
            self.queryset = self.queryset.filter(Q(receiver__pk=receiver_pk) | Q(sender__pk=receiver_pk)).order_by(
                "receiver", "sender", "created_datetime").distinct("receiver", "sender")

        else:
            self.queryset = TextMessage.objects.none()

    @action(detail=False, methods=["POST"], url_path="sending")
    def sending(self, request, sender=None, receiver=None):
        message = request.data.get("message")
        data = {"message": message, "sender_id": sender, "receiver_id": receiver}

        if sender in [None, ""]:
            return Response({"error": "Um eine Nachricht zu versenden muss ein Versender angegeben werden"})

        serializer = TextMessageSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReceiverTextMessageViewSet(viewsets.GenericViewSet, ListModelMixin):
    serializer_class = TextMessageSerializer
    queryset = TextMessage.objects.all()

    def get_queryset(self):
        self.filter_by_users()
        return self.queryset

    def filter_by_users(self):
        receiver_pk = self.kwargs.get("receiver")

        if receiver_pk not in ["", None]:
            self.queryset = self.queryset.filter(Q(receiver__pk=receiver_pk) | Q(sender__pk=receiver_pk))
        else:
            self.queryset = TextMessage.objects.none()

    @action(detail=False, methods=["GET"], url_path="latest-sender")
    def latest_sender(self, request, receiver=None):
        if receiver not in ["", None]:
            # self.queryset = self.queryset.filter(Q(receiver__pk=receiver) | Q(sender__pk=receiver)).order_by(
            #    "receiver", "sender", "created_datetime").distinct("receiver", "sender")
            # new subquery test
            subquery = TextMessage.objects.filter(
                Q(Q(sender__pk=OuterRef("sender"), receiver__pk=OuterRef("receiver")) |
                  Q(sender__pk=OuterRef("receiver"), receiver__pk=OuterRef("sender")))
            ).values("pk").order_by("created_datetime")[:1]
            self.queryset = self.queryset.filter(Q(receiver__pk=receiver) | Q(sender__pk=receiver)).annotate(
                latest_message_pk=Subquery(subquery)).order_by("latest_message_pk").distinct("latest_message_pk")
            print(self.queryset)
            for q in self.queryset:
                print(q.latest_message_pk)
        else:
            self.queryset = TextMessage.objects.none()
        page = self.paginate_queryset(self.queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
