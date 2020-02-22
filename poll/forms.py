from uniklinik.forms import BootstrapModelFormMixin
from poll.models import Poll, Option
from django import forms
from django.db.transaction import atomic


class PollForm(BootstrapModelFormMixin):
    class Meta:
        model = Poll
        fields = ("title", "description",)


class PollUpdateForm(BootstrapModelFormMixin):
    option = forms.CharField(required=False, label="Neue Option")

    class Meta:
        model = Poll
        fields = ("title", "description", "open", "option")

    @atomic
    def save(self, commit=True):
        option_title = self.cleaned_data.get("option")
        if option_title:
            new_option = Option(title=option_title)
            new_option.save()
            self.instance.option_set.add(new_option)
        return super().save(commit)
