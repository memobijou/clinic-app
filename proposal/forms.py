from uniklinik.forms import BootstrapModelFormMixin
from proposal.models import Type, Proposal


class TypeForm(BootstrapModelFormMixin):
    class Meta:
        model = Type
        fields = ("title",)


class ProposalForm(BootstrapModelFormMixin):
    class Meta:
        model = Proposal
        fields = ("confirmed", )
