from django.contrib.auth.models import User
from rest_framework import serializers
from account.models import Profile
from subject_area.models import SubjectArea
from subject_area.serializers import SubjectAreaSerializer
from django.utils.functional import lazy
import django.contrib.auth.password_validation as validators
from django.core import exceptions


class BasicUserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('pk', 'username', 'first_name', 'last_name', "email", "is_superuser", )


class BasicProfileSerializer(serializers.HyperlinkedModelSerializer):
    user = BasicUserSerializer()

    class Meta:
        model = Profile
        fields = ("is_admin", "user", )


def get_subject_area_choices():
    return SubjectArea.objects.values_list("pk", "title")


class ProfileSerializer(serializers.ModelSerializer):
    mentor = BasicUserSerializer(read_only=True)
    subject_area = SubjectAreaSerializer(read_only=True)
    subject_area_id = serializers.ChoiceField(
        source="subject_area.pk", allow_null=True, label="Fachrichtung (subject_area_id)",
        choices=lazy(get_subject_area_choices, tuple)())

    class Meta:
        model = Profile
        fields = ("is_admin", "mentor", "device_token", "subject_area", "subject_area_id", )
        read_only_fields = ('is_admin',)


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()
    students = BasicProfileSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('pk', 'username', 'first_name', 'last_name', "email", "is_superuser", "profile", "students", )

    def update(self, instance, validated_data):
        profile = validated_data.pop("profile")
        subject_area = profile.pop("subject_area")
        User.objects.filter(pk=instance.pk).update(**validated_data)
        Profile.objects.filter(pk=instance.profile.pk).update(**profile, subject_area_id=subject_area.get("pk"))
        instance.refresh_from_db()
        return instance


class UserPasswordSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField()

    class Meta:
        model = User
        fields = ('pk', 'username', "password", "password2", "email", "first_name", "last_name")
        extra_kwargs = {"email": {"required": True, "allow_null": False},
                        "first_name": {"required": True, "allow_null": False},
                        "last_name": {"required": True, "allow_null": False}
                        }

    def save(self):
        data = {**self.validated_data}
        data.pop("password2")
        user = User(**data)
        user.set_password(self.validated_data.get("password"))
        user.is_active = False
        user.save()
        return user

    def validate(self, data):
        if data.get("password2") != data.get("password"):
            raise serializers.ValidationError({"error": "Passwörter stimmen nicht überein"})
        try:
            password_validation_data = {**data}
            password_validation_data.pop("password2")
            validators.validate_password(password=data.get("password"), user=User(**password_validation_data))
        except exceptions.ValidationError as e:
            raise serializers.ValidationError({"error": list(e.messages)})
        return data


class SubjectAreaAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ("subject_area",)
