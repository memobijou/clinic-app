from django.db.models import Sum
from django.db.models.functions import Coalesce
from rest_framework import serializers
from account.models import Profile, AccountAuthorization
from subject_area.models import SubjectArea
from subject_area.serializers import SubjectAreaSerializer
from django.utils.functional import lazy
import django.contrib.auth.password_validation as validators
from django.core import exceptions
import os
from pyfcm import FCMNotification
from pyfcm.errors import AuthenticationError, FCMServerError, InvalidDataError, InternalPackageError
from django.contrib.auth.models import User
from account.models import title_choices


class BasicUserSerializer(serializers.HyperlinkedModelSerializer):
    title = serializers.CharField(source="profile.title")

    class Meta:
        model = User
        fields = ('pk', "title",  'username', 'first_name', 'last_name', "email", "is_superuser", "is_active",)


class BasicProfileSerializer(serializers.HyperlinkedModelSerializer):
    user = BasicUserSerializer()

    class Meta:
        model = Profile
        fields = ("is_admin", "user", "title", )


# def get_subject_area_choices():
#     return SubjectArea.objects.values_list("pk", "title")


class ProfileSerializer(serializers.ModelSerializer):
    mentor = BasicUserSerializer(read_only=True)
    subject_area = SubjectAreaSerializer(read_only=True)
    # subject_area_id = serializers.ChoiceField(
    #     source="subject_area.pk", allow_null=True, label="Fachrichtung (subject_area_id)",
    #     choices=lazy(get_subject_area_choices, tuple)())
    total_badges = serializers.SerializerMethodField()
    messaging_badges = serializers.SerializerMethodField()
    filestorage_badges = serializers.SerializerMethodField()

    def get_total_badges(self, instance):
        return instance.get_total_badges()

    def get_messaging_badges(self, instance: Profile):
        return instance.user.user_chat_push_histories.aggregate(
            total=Coalesce(Sum("unread_notifications"), 0)).get("total")

    def get_filestorage_badges(self, instance: Profile):
        return instance.user.fileuserhistory_set.aggregate(total=Coalesce(Sum("unread_notifications"), 0)).get("total")

    class Meta:
        model = Profile
        fields = ("title", "is_admin", "mentor", "device_token", "subject_area", "subject_area_id", "profile_image",
                  "appointment_badges", "task_badges", "total_badges", "filestorage_badges", "messaging_badges",)
        read_only_fields = ('is_admin',)


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()
    students = BasicProfileSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('pk', 'username', 'first_name', 'last_name', "email", "is_superuser", "profile", "students",
                  "is_active",)

    def update(self, instance, validated_data):
        profile = validated_data.pop("profile")
        print(f"bob: {profile}")
        User.objects.filter(pk=instance.pk).update(**validated_data)
        Profile.objects.filter(pk=instance.profile.pk).update(**profile)
        instance.refresh_from_db()
        return instance


class UserPasswordSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField()
    device_token = serializers.CharField()
    title = serializers.CharField(allow_null=True, required=False)

    class Meta:
        model = User
        fields = ('pk', 'username', "password", "password2", "email", "first_name", "last_name", "device_token",
                  "title",)
        extra_kwargs = {"email": {"required": True, "allow_null": False},
                        "first_name": {"required": True, "allow_null": False},
                        "last_name": {"required": True, "allow_null": False}
                        }

    def save(self):
        data = {**self.validated_data}
        print(f"hopps: {data}")
        device_token = data.pop("device_token")
        title = None
        if "title" in data:
            title = data.pop("title")
        data.pop("password2")
        user = User(**data)
        user.set_password(self.validated_data.get("password"))
        user.is_active = False
        user.save()
        user.profile.device_token = device_token
        if title:
            user.profile.title = title
        user.save()
        self.send_push_notifcation_to_new_user(user)
        return user

    def validate(self, data):
        if data.get("password2") != data.get("password"):
            raise serializers.ValidationError({"error": "Passwörter stimmen nicht überein"})
        try:
            print(f"hello: {data}")
            password_validation_data = {**data}
            password_validation_data.pop("device_token")
            if "title" in data:
                password_validation_data.pop("title")
            password_validation_data.pop("password2")
            validators.validate_password(password=data.get("password"), user=User(**password_validation_data))
        except exceptions.ValidationError as e:
            print(f"what is going on: {e.messages}")
            raise serializers.ValidationError({"error": list(e.messages)})
        return data

    @staticmethod
    def send_push_notifcation_to_new_user(user):
        print(os.environ.get("firebase_token"))
        if os.environ.get("firebase_token"):
            push_service = FCMNotification(api_key=os.environ.get("firebase_token"))
            try:
                r = push_service.notify_single_device(
                    registration_id=user.profile.device_token, message_title=f"Registrierung erfolgreich",
                    message_body=f"Sie müssen warten bis Ihr Account freigeschaltet wird",
                    sound="default", data_message={"category": "registration", "user_id": user.id})
                print(f"he: {r}")
                print("success registration")
            except (AuthenticationError, FCMServerError, InvalidDataError, InternalPackageError) as e:
                print(e)


class SubjectAreaAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ("subject_area",)


class DeviceTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ("device_token", )


class AuthorizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountAuthorization
        fields = ("email", )


class ProfileEditionSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source="user.first_name", required=False, allow_null=True)
    last_name = serializers.CharField(source="user.last_name", required=False, allow_null=True)

    class Meta:
        model = Profile
        fields = ("profile_image", "title", "first_name", "last_name")

    def update(self, instance, validated_data):
        print(f"yes {validated_data}")
        title = validated_data.get("title")
        profile_image = validated_data.get("profile_image")
        first_name = None
        last_name = None

        if "user" in validated_data:
            user_data = validated_data.pop("user")
            first_name = user_data.get('first_name')
            last_name = user_data.get('last_name')
        user = instance.user

        if title:
            instance.title = title

        if profile_image:
            instance.profile_image = profile_image

        if first_name:
            user.first_name = first_name

        if last_name:
            user.last_name = last_name

        if first_name or last_name:
            user.save()
        instance.save()
        return instance
