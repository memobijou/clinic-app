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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fields["title"].required = True
        self.fields["title"].widget.attrs["required"] = "required"

    @atomic
    def save(self, commit=True):
        option_title = self.cleaned_data.get("option")
        if option_title:
            new_option = Option(title=option_title)
            new_option.save()
            self.instance.option_set.add(new_option)
        return super().save(commit)

    def clean_open(self):
        open_value = self.cleaned_data.get("open")
        if open_value is True:
            if self.instance.option_set.count() == 0:
                option = self.data.get("option")
                print(f"bananana: {option}")
                if not option:
                    self.add_error(
                        "open", "Sie müssen der Umfrage erst eine Option zuweisen, um diese veröffentlichen zu können.")
        return open_value


class OptionForm(BootstrapModelFormMixin):
    class Meta:
        model = Option
        fields = ("title",)
