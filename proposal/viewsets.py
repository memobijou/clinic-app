from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, CreateModelMixin
from proposal.models import Proposal
from proposal.serializers import ProposalSerializer


class ProposalViewset(GenericViewSet, ListModelMixin, CreateModelMixin):
    serializer_class = ProposalSerializer

    def get_queryset(self):
        return Proposal.objects.filter(user_id=self.kwargs.get("user_id"))
