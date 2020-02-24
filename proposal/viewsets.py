from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, CreateModelMixin
from proposal.models import Proposal, Type
from proposal.serializers import ProposalSerializer, TypeSerializer


class ProposalViewset(GenericViewSet, ListModelMixin, CreateModelMixin):
    serializer_class = ProposalSerializer

    def get_queryset(self):
        return Proposal.objects.filter(user_id=self.kwargs.get("user_id"))


class TypeViewset(GenericViewSet, ListModelMixin):
    serializer_class = TypeSerializer

    def get_queryset(self):
        return Type.objects.all()
