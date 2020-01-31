from subject_area.models import SubjectArea, Category
from uniklinik.forms import BootstrapModelFormMixin


class SubjectAreaForm(BootstrapModelFormMixin):
    class Meta:
        model = SubjectArea
        fields = ("title", )


class CategoryForm(BootstrapModelFormMixin):
    class Meta:
        model = Category
        fields = ("title", )
