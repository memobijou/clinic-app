from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User
from django import forms
from django.db import transaction

from account.models import title_choices
from subject_area.models import SubjectArea
from uniklinik.forms import BootstrapModelFormMixin


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'first_name', 'last_name', "email", "is_superuser")

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["mentor"] = forms.ModelChoiceField(queryset=User.objects.exclude(pk=self.instance.pk),
                                                       label="Mentor", required=False)
        self.fields["subject_area"] = forms.ModelChoiceField(queryset=SubjectArea.objects.all(), label="Fachrichtung",
                                                             required=False)
        self.fields["title"] = forms.ChoiceField(choices=title_choices, label="Titel", required=False)

        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-control"

    @transaction.atomic
    def save(self, commit=True):
        mentor = self.cleaned_data.get("mentor")
        subject_area = self.cleaned_data.get("subject_area")
        title = self.cleaned_data.get("title")
        instance = super().save(commit)
        profile = instance.profile
        profile.mentor = mentor
        profile.subject_area = subject_area
        profile.title = title
        instance.save()
        return instance


class EditForm(CustomUserCreationForm):
    def clean_is_superuser(self):
        is_superuser = self.cleaned_data.get("is_superuser")
        if self.instance.is_superuser is True and (is_superuser is False or is_superuser is None):
            self.add_error("is_superuser", "Ein Administrator kann diese Eigenschaft nicht abwählen")
        return is_superuser

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(user=user, *args, **kwargs)
        self.fields["is_superuser"].widget.attrs["class"] = ""
        self.fields["is_superuser"].widget.attrs["style"] = "cursor:pointer;"
        self.fields["password1"].required = False
        self.fields["password2"].required = False

        if self.instance:
            profile = self.instance.profile
            self.fields["subject_area"].initial = profile.subject_area
            self.fields["mentor"].initial = profile.mentor
            self.fields["title"].initial = profile.title

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 == "" and password2 == "":
            return password2
        return super().clean_password2()

    def save(self, commit=True):
        old_password = self.instance.password
        instance = super().save(commit=False)
        instance._password = old_password
        instance.password = old_password
        instance.save()
        return instance


class ProfileFormMixin(BootstrapModelFormMixin):
    biography = forms.CharField(widget=forms.Textarea(), label="Biografie", required=False)
    is_admin = forms.BooleanField(label="Adminstrator", required=False)
    title = forms.ChoiceField(choices=title_choices, label="Titel", required=False)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'is_superuser',)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.instance:
            profile = self.instance.profile
            self.fields["biography"].initial = profile.biography
            self.fields["is_admin"].initial = profile.is_admin
            self.fields["title"].initial = profile.title

    def save(self, commit=True):
        instance = super().save()
        biography = self.cleaned_data.get("biography")
        is_admin = self.cleaned_data.get("is_admin")
        title = self.cleaned_data.get("title")
        profile = instance.profile
        profile.biography = biography
        profile.is_admin = is_admin
        profile.title = title
        profile.save()
        return instance


class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = None

    def clean_old_password(self):
        return self.cleaned_data.get("old_password")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-control"
