from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User
from django import forms

from uniklinik.forms import BootstrapModelFormMixin


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'first_name', 'last_name', "email", "is_superuser")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-control"


class EditBaseForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', "email", "is_superuser", 'password1', 'password2',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-control"
        self.fields["is_superuser"].widget.attrs["class"] = ""
        self.fields["is_superuser"].widget.attrs["style"] = "cursor:pointer;"

    def clean_is_superuser(self):
        print(f" ????? 1!!!")
        is_superuser = self.cleaned_data.get("is_superuser")
        print(is_superuser)
        print(self.instance.is_superuser)
        if self.instance.is_superuser is True and (is_superuser is False or is_superuser is None):
            self.add_error("is_superuser", "Ein Administrator kann diese Eigenschaft nicht abwählen")
        return is_superuser


class ProfileFormMixin(BootstrapModelFormMixin):
    biography = forms.CharField(widget=forms.Textarea(), label="Biografie", required=False)
    is_admin = forms.BooleanField(label="Adminstrator", required=False)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', "email", "is_superuser", )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.instance:
            print(f"wwwww: {self.instance} {self.instance.profile.biography}")
            self.fields["biography"].initial = self.instance.profile.biography
            self.fields["is_admin"].initial = self.instance.profile.is_admin

    def save(self, commit=True):
        instance = super().save()
        biography = self.cleaned_data.get("biography")
        is_admin = self.cleaned_data.get("is_admin")
        instance.profile.biography = biography
        instance.profile.is_admin = is_admin
        instance.profile.save()
        return instance


class EditForm(EditBaseForm):
    def __init__(self, user=None, **kwargs):
        super().__init__(**kwargs)
        print(user.first_name + user.email)
        self.fields["password1"].required = False
        self.fields["password2"].required = False
        self.fields["mentor"] = forms.ModelChoiceField(
            queryset=User.objects.exclude(pk=user.pk), label="Mentor", initial=self.instance.profile.mentor,
            required=False)

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 == "" and password2 == "":
            return password2
        return super().clean_password2()

    def save(self, commit=True):
        mentor = self.cleaned_data.get("mentor")
        print(f"clue: {mentor}")
        self.instance.profile.mentor = mentor
        password1 = self.cleaned_data["password1"]
        if password1 == "":
            user = self.instance.save()
            return user
        return super().save(commit)


class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = None

    def clean_old_password(self):
        return self.cleaned_data.get("old_password")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-control"
