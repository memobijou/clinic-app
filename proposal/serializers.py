from rest_framework import serializers

from proposal.models import Proposal, Type


class ProposalSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    title = serializers.CharField(source="type.title", read_only=True)

    class Meta:
        model = Proposal
        fields = ("pk", "user", "first_name", "last_name", "start_date", "end_date", "confirmed", "type", "title")
        extra_kwargs = {
            'user': {'write_only': True},
            'confirmed': {"read_only": True}
        }


class TypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Type
        fields = ("pk", "title",)
