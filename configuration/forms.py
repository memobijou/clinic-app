from django import forms


class ConfigForm(forms.Form):
    company_title = forms.CharField(label="Firmentitel")
    logo = forms.FileField(label="Neues Firmenlogo hochladen")
    theme_color = forms.ChoiceField(choices=(('blauweiss', 'blauweiss'),), label="Theme")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for visible in self.visible_fields():
            if isinstance(visible.field, forms.FileField) is False:
                visible.field.widget.attrs["class"] = "form-control"
