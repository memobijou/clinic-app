from django.db.models import Q
from rest_framework import serializers, viewsets
from rest_framework.pagination import LimitOffsetPagination
from account.serializers import UserSerializer
from messaging.models import TextMessage


class TextMessageSerializer(serializers.HyperlinkedModelSerializer):
    sender = UserSerializer()
    receiver = UserSerializer()

    class Meta:
        model = TextMessage
        fields = ("pk", "sender", "receiver", "message", "created_datetime", )


class TextMessageViewset(viewsets.ModelViewSet):
    queryset = TextMessage.objects.all()
    serializer_class = TextMessageSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        self.filter_by_users()
        return self.queryset.order_by("created_datetime")

    def filter_by_users(self):
        user1_pk = self.kwargs.get("user1")
        user2_pk = self.kwargs.get("user2")

        if user1_pk and user2_pk not in ["", None]:
            self.queryset = self.queryset.filter(
                Q(Q(Q(receiver__pk=user1_pk) & Q(sender__pk=user2_pk)) |
                  Q(Q(receiver__pk=user2_pk) & Q(sender__pk=user1_pk))))
