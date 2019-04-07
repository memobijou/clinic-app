from django import forms


class BootstrapModelFormMixin(forms.ModelForm):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for visible in self.visible_fields():
            if isinstance(visible.field, forms.ModelMultipleChoiceField) is False:
                visible.field.widget.attrs["class"] = "form-control"
