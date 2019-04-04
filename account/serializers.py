from rest_framework.pagination import LimitOffsetPagination
from django.contrib.auth.models import User
from rest_framework import serializers, viewsets
from account.models import Profile


class BasicUserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('pk', 'username', 'first_name', 'last_name', "email", "is_superuser", )


class BasicProfileSerializer(serializers.HyperlinkedModelSerializer):
    user = BasicUserSerializer()

    class Meta:
        model = Profile
        fields = ("is_admin", "user", )


class ProfileSerializer(serializers.HyperlinkedModelSerializer):
    mentor = BasicUserSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = ("is_admin", "mentor", "device_token", )
        read_only_fields = ('is_admin',)


class UserSerializer(serializers.HyperlinkedModelSerializer):
    profile = ProfileSerializer()
    students = BasicProfileSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('pk', 'username', 'first_name', 'last_name', "email", "is_superuser", "profile", "students", )

    def update(self, instance, validated_data):
        profile = validated_data.pop("profile")
        User.objects.filter(pk=instance.pk).update(**validated_data)
        Profile.objects.filter(pk=instance.profile.pk).update(**profile)
        instance.refresh_from_db()
        return instance


# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        self.filter_by_pk()
        return self.queryset

    def filter_by_pk(self):
        pk_filter_value = self.request.GET.get("pk")
        if pk_filter_value is not None and pk_filter_value != "":
            self.queryset = self.queryset.filter(pk=pk_filter_value)
