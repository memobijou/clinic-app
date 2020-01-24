from rest_framework.serializers import ModelSerializer
from broadcast.models import Broadcast, Like
from account.serializers import UserSerializer
from rest_framework import serializers
from django.contrib.auth.models import User


class MinimalUserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email")


class LikeSerializer(ModelSerializer):
    class Meta:
        model = Like
        fields = ("id", "user", "like_datetime")


class BroadcastSerializer(ModelSerializer):
    sender_id = serializers.IntegerField(write_only=True)
    sender = MinimalUserSerializer(read_only=True)
    likes = LikeSerializer(many=True, read_only=True, source="like_set")
    likes_count = serializers.SerializerMethodField()

    class Meta:
        model = Broadcast
        fields = ("text", "sender_id", "sender", "send_datetime", "likes", "likes_count")

    def get_likes_count(self, obj):
        return obj.like_set.count()
