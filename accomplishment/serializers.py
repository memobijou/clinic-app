from rest_framework import serializers, viewsets
from rest_framework.pagination import LimitOffsetPagination
from accomplishment.models import Accomplishment, UserAccomplishment
from account.models import Group
from account.serializers import UserSerializer


class AccomplishmentGroupSerializer(serializers.HyperlinkedModelSerializer):
    users = UserSerializer(many=True)

    class Meta:
        model = Group
        fields = ("pk", 'name', "users")


class AccomplishmentUserSerializer(serializers.HyperlinkedModelSerializer):
    user = UserSerializer()

    class Meta:
        model = UserAccomplishment
        fields = ("pk", 'score', 'user',)


class AccomplishmentSerializer(serializers.HyperlinkedModelSerializer):
    groups = AccomplishmentGroupSerializer(many=True)
    user_accomplishments = AccomplishmentUserSerializer(many=True)

    class Meta:
        model = Accomplishment
        fields = ("pk", "name", "full_score", "groups", "user_accomplishments", )


class AccomplishmentViewSet(viewsets.ModelViewSet):
    queryset = Accomplishment.objects.all()
    serializer_class = AccomplishmentSerializer
    pagination_class = LimitOffsetPagination
