from django.db.models import OuterRef, Subquery
from django.db.models.functions import Coalesce
from rest_framework import serializers
from django.contrib.auth.models import User
from account.models import Profile, Group
from messaging.models import TextMessage, ChatPushHistory


# ID, first_name, last_name, username, profile_image
# Group nur pk, name schicken

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ("pk", "title", )


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ('pk', 'username', 'first_name', 'last_name', "profile",)


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ("pk", "name", "color",)


class TextMessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)
    group = GroupSerializer(read_only=True)
    sender_id = serializers.IntegerField(write_only=True)
    receiver_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = TextMessage
        fields = ("pk", "receiver", "sender", "group", "message", "created_datetime", "sender_id", "receiver_id",)


class GroupTextMessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    group = GroupSerializer(read_only=True)
    sender_id = serializers.IntegerField(write_only=True)
    group_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = TextMessage
        fields = ("pk", "sender", "group", "message", "created_datetime", "sender_id", "group_id",)


class ReceiverTextMessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)
    group = GroupSerializer(read_only=True)
    sender_id = serializers.IntegerField(write_only=True)
    receiver_id = serializers.IntegerField(write_only=True)
    unread_notifications = serializers.IntegerField(read_only=True)

    class Meta:
        model = TextMessage
        fields = ("pk", "receiver", "sender", "group", "message", "created_datetime", "sender_id", "receiver_id",
                  "unread_notifications",)
