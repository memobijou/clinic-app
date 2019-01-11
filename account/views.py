from django.contrib.auth import password_validation
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.views import View
from django import forms


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'first_name', 'last_name', "email", "is_superuser")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-control"


class CreateUserView(LoginRequiredMixin, generic.CreateView):
    form_class = CustomUserCreationForm
    template_name = "account/user/new_user.html"
    success_url = reverse_lazy("account:user_list")


class UserListView(LoginRequiredMixin, generic.ListView):
    template_name = "account/user/user_list.html"
    paginate_by = 15
    queryset = User.objects.all()


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', "email", "is_superuser")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-control"
        self.fields["is_superuser"].widget.attrs["class"] = ""
        self.fields["is_superuser"].widget.attrs["style"] = "cursor:pointer;"
        if self.instance.is_superuser is True:
            pass
        print(self.instance.email)

    def clean_is_superuser(self):
        print(f" ????? 1!!!")
        is_superuser = self.cleaned_data.get("is_superuser")
        print(is_superuser)
        print(self.instance.is_superuser)
        if self.instance.is_superuser is True and (is_superuser is False or is_superuser is None):
            self.add_error("is_superuser", "Ein Administrator kann diese Eigenschaft nicht abwählen")
        return is_superuser


class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = None

    def clean_old_password(self):
        return self.cleaned_data.get("old_password")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-control"


class UserProfileView(LoginRequiredMixin, generic.UpdateView):
    template_name = "account/user/profile/profile.html"
    form_class = ProfileForm

    def __init__(self):
        super().__init__()
        self.password_form = None
        self.object = None

    def dispatch(self, request, *args, **kwargs):
        self.password_form = self.get_password_form()
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        self.object = User.objects.get(pk=self.kwargs.get("pk"))
        print(self.object.username)
        return self.object

    def get_password_form(self):
        if self.request.method == "POST":
            password_form = CustomPasswordChangeForm(self.object)
        else:
            password_form = CustomPasswordChangeForm(self.object)
        return password_form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"password_form": self.password_form})
        return context

    def get_success_url(self):
        return reverse_lazy("account:user_profile", kwargs={"pk": self.kwargs.get("pk")})


class ChangeUserPasswordView(LoginRequiredMixin, View):
    template_name = "account/user/profile/profile.html"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.object = None
        self.form = None
        self.password_form = None

    def dispatch(self, request, *args, **kwargs):
        if self.request.method == "GET":
            return HttpResponseRedirect(self.get_profile_url())
        self.object = User.objects.get(pk=self.kwargs.get("pk"))
        print(f"why: {self.object.username}")
        self.password_form = self.get_password_form()
        self.form = self.get_form()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if self.password_form.is_valid() is True:
            self.password_form.save()
            return HttpResponseRedirect(self.get_profile_url())
        else:
            return render(request, self.template_name, self.get_context())

    def get_form(self):
        if self.request.method == "POST":
            self.form = ProfileForm(instance=self.object)
        else:
            self.form = ProfileForm(instance=self.object)
        return self.form

    def get_password_form(self):
        if self.request.method == "POST":
            self.password_form = CustomPasswordChangeForm(self.object, self.request.POST)
        else:
            self.password_form = CustomPasswordChangeForm(self.object)
        return self.password_form

    def get_context(self):
        context = {"object": self.object, "password_form": self.password_form, "form": self.form}
        return context

    def get_profile_url(self):
        return reverse_lazy("account:user_profile", kwargs={"pk": self.kwargs.get("pk")})
