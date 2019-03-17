from rest_framework.pagination import LimitOffsetPagination

from django.contrib.auth.models import User
from rest_framework import serializers, viewsets

from accomplishment.models import UserAccomplishment
from account.models import Profile


class BasicUserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('pk', 'username', 'first_name', 'last_name', "email", "is_superuser", )


class ProfileSerializer(serializers.HyperlinkedModelSerializer):
    mentor = BasicUserSerializer()

    class Meta:
        model = Profile
        fields = ("is_admin", "mentor", )


class UserAccomplishmentSerializer(serializers.HyperlinkedModelSerializer):
    user = BasicUserSerializer()

    class Meta:
        model = UserAccomplishment
        fields = ("pk", "user", )


class UserSerializer(serializers.HyperlinkedModelSerializer):
    profile = ProfileSerializer()
    students = UserAccomplishmentSerializer(many=True)

    class Meta:
        model = User
        fields = ('pk', 'username', 'first_name', 'last_name', "email", "is_superuser", "profile", "students", )


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
