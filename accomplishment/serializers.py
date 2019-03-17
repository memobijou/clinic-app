from rest_framework import serializers, viewsets
from rest_framework.pagination import LimitOffsetPagination
from accomplishment.models import Accomplishment, UserAccomplishment
from account.models import Group
from account.serializers import UserSerializer


# class AccomplishmentGroupSerializer(serializers.HyperlinkedModelSerializer):
#     users = UserSerializer(many=True)
#
#     class Meta:
#         model = Group
#         fields = ("pk", 'name', "users")


class BasicUserAccomplishmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAccomplishment
        fields = ("pk", 'score', "user", "accomplishment" )


class UserAccomplishmentSerializer(serializers.HyperlinkedModelSerializer):
    user = UserSerializer()

    class Meta:
        model = UserAccomplishment
        fields = ("pk", 'score', 'user', )


class AccomplishmentSerializer(serializers.HyperlinkedModelSerializer):
    # groups = AccomplishmentGroupSerializer(many=True)
    user_accomplishments = UserAccomplishmentSerializer(many=True)

    class Meta:
        model = Accomplishment
        fields = ("pk", "name", "full_score", "user_accomplishments",)


class AccomplishmentViewSet(viewsets.ModelViewSet):
    queryset = Accomplishment.objects.all()
    serializer_class = AccomplishmentSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        user_id = self.request.GET.get("user_id")
        if user_id:
            self.queryset = self.queryset.filter(user_accomplishments__user__pk=user_id)
        print(self.queryset.values())
        return self.queryset


class UserAccomplishmentViewSet(viewsets.ModelViewSet):
    queryset = UserAccomplishment.objects.all()
    serializer_class = BasicUserAccomplishmentSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        user_id = self.request.GET.get("user_id")
        if user_id:
            self.queryset = self.queryset.filter(user_id=user_id)
        return self.queryset
