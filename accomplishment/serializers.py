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
        fields = ("pk", 'score', "user", "accomplishment", )


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
        fields = ("pk", "name", "full_score", "user_accomplishments", )


class AccomplishmentViewSet(viewsets.ModelViewSet):
    queryset = Accomplishment.objects.all()
    serializer_class = AccomplishmentSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        user_id = self.request.GET.get("user_id")
        pk = self.request.GET.get("pk")
        group_id = self.request.GET.get("group_id")

        if pk:
            self.queryset = self.queryset.filter(pk=pk)

        if user_id:
            self.queryset = self.queryset.filter(groups__users__pk=user_id).distinct()

        if group_id:
            self.queryset = self.queryset.filter(groups__pk=group_id).distinct()

        return self.queryset


class UserAccomplishmentViewSet(viewsets.ModelViewSet):
    queryset = UserAccomplishment.objects.all()
    serializer_class = BasicUserAccomplishmentSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        user_id = self.request.GET.get("user_id")
        accomplishment_id = self.request.GET.get("accomplishment_id")

        if user_id:
            self.queryset = self.queryset.filter(user_id=user_id)

        if accomplishment_id:
            self.queryset = self.queryset.filter(accomplishment_id=accomplishment_id)

        return self.queryset
