from rest_framework import serializers
from account.serializers import UserSerializer
from messaging.models import TextMessage


class TextMessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)
    sender_id = serializers.IntegerField(write_only=True)
    receiver_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = TextMessage
        fields = ("pk", "receiver", "sender", "message", "created_datetime", "sender_id", "receiver_id", )
