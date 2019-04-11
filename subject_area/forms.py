from subject_area.models import SubjectArea
from uniklinik.forms import BootstrapModelFormMixin


class SubjectAreaForm(BootstrapModelFormMixin):
    class Meta:
        model = SubjectArea
        fields = ("title", )
