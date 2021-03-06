from rest_framework.serializers import ModelSerializer

from account.models import title_choices
from broadcast.models import Broadcast, Like, Comment, Attachement
from account.serializers import UserSerializer
from rest_framework import serializers
from django.contrib.auth.models import User


class MinimalUserSerializer(ModelSerializer):
    title = serializers.ChoiceField(choices=title_choices, source="profile.title")
    profile_image = serializers.ImageField(source="profile.profile_image")

    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name", "title", "profile_image")


class LikeSerializer(ModelSerializer):
    class Meta:
        model = Like
        fields = ("id", "user", "like_datetime")


class CommentSerializer(ModelSerializer):
    sender_id = serializers.IntegerField(write_only=True)
    sender = MinimalUserSerializer(read_only=True)
    # likes = LikeSerializer(many=True, read_only=True, source="like_set")
    # likes_count = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ("pk", "text", "sender_id", "sender", "send_datetime",)  # "likes", "likes_count")

    # def get_likes_count(self, obj):
        # return obj.like_set.count()


class AttachementSerializer(ModelSerializer):
    class Meta:
        model = Attachement
        fields = ("file", "upload_datetime", )


class BroadcastSerializer(ModelSerializer):
    sender_id = serializers.IntegerField(write_only=True)
    sender = MinimalUserSerializer(read_only=True)
    likes = LikeSerializer(many=True, read_only=True, source="like_set")
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    comments = CommentSerializer(many=True, read_only=True, source="comment_set")
    attachements = AttachementSerializer(many=True, read_only=True, source="attachement_set")

    class Meta:
        model = Broadcast
        fields = ("id", "text", "sender_id", "sender", "send_datetime", "likes", "likes_count",
                  "comments_count", "comments", "attachements")

    def get_likes_count(self, obj):
        return obj.like_set.count()

    def get_comments_count(self, obj):
        return obj.comment_set.count()
