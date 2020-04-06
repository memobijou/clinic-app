from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, CreateModelMixin
from proposal.models import Proposal, Type
from proposal.serializers import ProposalSerializer, TypeSerializer
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User


class ProposalViewset(GenericViewSet, ListModelMixin, CreateModelMixin):
    serializer_class = ProposalSerializer

    def get_queryset(self):
        if self.kwargs.get("user_id"):
            user = get_object_or_404(User, pk=self.kwargs.get("user_id"))
            profile = user.profile
            profile.proposal_badges = 0
            profile.save()
        return Proposal.objects.filter(user_id=self.kwargs.get("user_id"))


class TypeViewset(GenericViewSet, ListModelMixin):
    serializer_class = TypeSerializer

    def get_queryset(self):
        return Type.objects.all()
