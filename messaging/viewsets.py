from django.db.models import Q, Subquery, OuterRef
from django.db.models.functions import Coalesce
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from messaging.models import TextMessage, ChatPushHistory
from account.models import Group
from messaging.serializers import TextMessageSerializer, GroupTextMessageSerializer, ReceiverTextMessageSerializer
from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import ModelViewSet
from django.contrib.auth.models import User
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from messaging.utils import send_push_notification_to_receiver, send_push_notification_to_group
from django.db.transaction import atomic


text_message_page_size = 20


class CustomPagination(PageNumberPagination):
    page_size = text_message_page_size


class TextMessageViewset(viewsets.GenericViewSet, ListModelMixin):
    serializer_class = TextMessageSerializer
    queryset = TextMessage.objects.all()
    pagination_class = CustomPagination

    def get_queryset(self):
        self.filter_by_users()
        # if self.kwargs.get("receiver"):
        #     user = get_object_or_404(User, pk=self.kwargs.get("receiver"))
        #     user.profile.messaging_badges = 0
        #     user.profile.save()
        pagenum = self.request.query_params.get('page', 1)
        if pagenum == 1:
            receiver_id = self.kwargs.get("receiver")
            sender_id = self.kwargs.get("sender")

            if receiver_id and sender_id:
                ChatPushHistory.objects.filter(
                    user_id=receiver_id, participant_id=sender_id
                ).update(unread_notifications=0)
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

            sender = User.objects.get(pk=sender)
            receiver = User.objects.get(pk=receiver)
            send_push_notification_to_receiver(message, sender, receiver)
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["POST"], url_path="group-sending")
    def group_sending(self, request, sender=None, receiver=None):
        group = receiver
        message = request.data.get("message")
        data = {"message": message, "sender_id": sender, "group_id": receiver}
        print(f"brown: {data}")
        if sender in [None, ""]:
            return Response({"error": "Um eine Nachricht zu versenden muss ein Versender angegeben werden"})

        serializer = GroupTextMessageSerializer(data=data)

        if serializer.is_valid():
            serializer.save()

            sender = User.objects.get(pk=sender)
            group = Group.objects.get(pk=group)

            send_push_notification_to_group(message, sender, group)
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReceiverTextMessageViewSet(viewsets.GenericViewSet, ListModelMixin):
    serializer_class = ReceiverTextMessageSerializer
    queryset = TextMessage.objects.all()

    def get_queryset(self):
        self.filter_by_users()
        subquery_push_history = ChatPushHistory.objects.filter(
            Q(
                Q(user_id=OuterRef("receiver_id"), participant_id=OuterRef("sender_id"), group_id=None) |
                Q(user_id=self.kwargs.get("receiver"), participant_id=None, group_id=OuterRef("group_id"))
            )
        ).values("unread_notifications")[:1]
        self.queryset = self.queryset.annotate(unread_notifications=Coalesce(Subquery(subquery_push_history), 0))
        print(f"banana {type(self.queryset.first().group_id)}")
        return self.queryset

    def filter_by_users(self):
        receiver_pk = self.kwargs.get("receiver")

        if receiver_pk not in ["", None]:
            self.queryset = self.queryset.filter(Q(receiver__pk=receiver_pk) | Q(sender__pk=receiver_pk) |
                                                 Q(group__users__id=receiver_pk))
        else:
            self.queryset = TextMessage.objects.none()

    @action(detail=False, methods=["GET"], url_path="latest-sender")
    def latest_sender(self, request, receiver=None):
        self.queryset = self.get_queryset()  # not called in custom action

        print(f"apple: {self.queryset.first().unread_notifications}")

        if receiver not in ["", None]:
            subquery = TextMessage.objects.filter(
                Q(Q(sender__pk=OuterRef("sender"), receiver__pk=OuterRef("receiver")) |
                  Q(sender__pk=OuterRef("receiver"), receiver__pk=OuterRef("sender"))
                  )
            ).order_by("-created_datetime").values("pk")[:1]

            latest_messages = self.queryset.values("sender", "receiver").exclude(
                group__isnull=False, receiver__isnull=True).filter(
                Q(Q(receiver_id=receiver) | Q(sender_id=receiver))).annotate(
                pk=Subquery(subquery)).values_list("pk", flat=True)

            group_subquery = TextMessage.objects.filter(group_id=OuterRef("group_id")).order_by(
                "-created_datetime").values("pk")[:1]

            latest_group_messages = self.queryset.values("group").distinct("group").\
                exclude(group__exact=None).filter(
                receiver__exact=None, group__users__id=receiver
            ).order_by("group").annotate(
                pk=Subquery(group_subquery)
            ).values_list("pk", flat=True)

            self.queryset = self.queryset.filter(Q(Q(pk__in=latest_messages) | Q(pk__in=latest_group_messages)))
        else:
            self.queryset = TextMessage.objects.none()
        page = self.paginate_queryset(self.queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)


class GroupTextMessageViewSet(viewsets.GenericViewSet, ListModelMixin):
    serializer_class = TextMessageSerializer
    queryset = TextMessage.objects.all()

    def get_queryset(self):
        self.filter_by_group()

        pagenum = self.request.query_params.get('page', 1)
        if pagenum == 1:
            group_id = self.kwargs.get("group")
            user_id = self.kwargs.get("user")

            if group_id:
                ChatPushHistory.objects.filter(
                    user_id=user_id, group_id=group_id
                ).update(unread_notifications=0)

        return self.queryset

    def filter_by_group(self):
        group_pk = self.kwargs.get("group")

        if group_pk not in ["", None]:
            self.queryset = self.queryset.filter(group__pk=group_pk)
        else:
            self.queryset = TextMessage.objects.none()
