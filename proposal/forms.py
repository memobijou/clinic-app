from uniklinik.forms import BootstrapModelFormMixin
from proposal.models import Type


class TypeForm(BootstrapModelFormMixin):
    class Meta:
        model = Type
        fields = ("title",)
