from abc import ABCMeta, abstractmethod
from django.db.models import Q
from rest_framework import serializers, viewsets
from rest_framework.pagination import PageNumberPagination
from account.serializers import UserSerializer
from messaging.models import TextMessage


class ReadOnlyTextMessageSerializer(serializers.HyperlinkedModelSerializer):
    sender = UserSerializer()
    receiver = UserSerializer()

    class Meta:
        model = TextMessage
        fields = ("pk", "sender", "receiver", "message", "created_datetime", )


class TextMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TextMessage
        fields = ("pk", "sender", "receiver", "message", "created_datetime", )


class BaseTextMessageViewset(metaclass=ABCMeta):
    kwargs = None
    queryset = TextMessage.objects.all()
    pagination_class = PageNumberPagination

    @property
    @abstractmethod
    def serializer_class(self):
        pass

    def get_queryset(self):
        self.filter_by_users()
        return self.queryset

    def filter_by_users(self):
        user1_pk = self.kwargs.get("user1")
        user2_pk = self.kwargs.get("user2")

        if user1_pk and user2_pk not in ["", None]:
            self.queryset = self.queryset.filter(
                Q(Q(Q(receiver__pk=user1_pk) & Q(sender__pk=user2_pk)) |
                  Q(Q(receiver__pk=user2_pk) & Q(sender__pk=user1_pk))))


class ReadOnlyTextMessageViewset(BaseTextMessageViewset, viewsets.ReadOnlyModelViewSet):
    serializer_class = ReadOnlyTextMessageSerializer


class TextMessageViewset(BaseTextMessageViewset, viewsets.ModelViewSet):
    serializer_class = TextMessageSerializer

