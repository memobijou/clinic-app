from accomplishment.models import Accomplishment
from uniklinik.forms import BootstrapModelForm
from django import forms
from account.models import Group


class AccomplishmentForm(BootstrapModelForm):
    groups = forms.ModelMultipleChoiceField(queryset=Group.objects.all(),
                                            widget=forms.CheckboxSelectMultiple
                                            )

    class Meta:
        model = Accomplishment
        fields = ("name", "groups", "full_score")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # self.fields["groups"].widget
        self.fields["full_score"].widget.attrs["step"] = 5

    def clean_full_score(self):
        full_score = self.cleaned_data.get("full_score")
        full_score = int(full_score)
        if full_score % 5 != 0:
            self.add_error("full_score", "Die Punktezahl muss in fünfer Schritte angegeben werden")
        return full_score
