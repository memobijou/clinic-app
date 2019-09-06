from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.db import transaction
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.
from django.views import View
from abc import ABCMeta, abstractmethod
from account.forms import CustomUserCreationForm, ProfileFormMixin, CustomPasswordChangeForm, EditForm, \
    CustomAuthenticationForm, AccountAuthorizationForm
from account.models import Profile, AccountAuthorization
from django.contrib.auth.models import User
import json
import requests
import os


class CreateUserView(LoginRequiredMixin, generic.CreateView):
    form_class = CustomUserCreationForm
    template_name = "account/user/new_user/new_user.html"
    success_url = reverse_lazy("account:user_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class UserListView(LoginRequiredMixin, generic.ListView):
    template_name = "account/user/user_list/user_list.html"
    paginate_by = 15
    queryset = User.objects.all()


class UserEditBaseView(LoginRequiredMixin, generic.UpdateView, metaclass=ABCMeta):
    @property
    @abstractmethod
    def form_class(self):
        pass

    @property
    @abstractmethod
    def template_name(self):
        pass

    @abstractmethod
    def get_success_url(self):
        pass

    def __init__(self):
        super().__init__()
        self.password_form = None
        self.object = None

    def dispatch(self, request, *args, **kwargs):
        self.password_form = self.get_password_form()
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        self.object = User.objects.get(pk=self.kwargs.get("pk"))
        return self.object

    def get_password_form(self):
        password_form = CustomPasswordChangeForm(self.object)
        return password_form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"password_form": self.password_form})
        return super().get_context_data(**context)

    def form_valid(self, form):
        form = self.custom_form_validation(form)
        if form.is_valid() is False:
            return super().form_invalid(form)
        return super().form_valid(form)

    def custom_form_validation(self, form):
        form = self.dont_allow_superuser_to_be_changed_from_non_superuser(form)
        return form

    def dont_allow_superuser_to_be_changed_from_non_superuser(self, form):
        instance = form.save(commit=False)
        if instance.is_superuser:
            if not self.request.user.is_superuser:
                form.add_error(None, "Sie haben keine Berechtigung diesen Nutzer zu bearbeiten")
        return form


class UserProfileView(UserEditBaseView):
    form_class = ProfileFormMixin
    template_name = "account/user/profile/profile.html"

    def get_success_url(self):
        return reverse_lazy("account:user_profile", kwargs={"pk": self.kwargs.get("pk")})


class UserEditView(UserEditBaseView):
    form_class = EditForm
    template_name = "account/user/edit/edit.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse_lazy("account:user_edit", kwargs={"pk": self.kwargs.get("pk")})


class BaseChangePasswordView(LoginRequiredMixin, View):
    @property
    @abstractmethod
    def template_name(self):
        pass

    @abstractmethod
    def get_form(self):
        pass

    @abstractmethod
    def get_success_url(self):
        pass

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.password_form = None
        self.object = None
        self.form = None

    def dispatch(self, request, *args, **kwargs):
        if self.request.method == "GET":
            return HttpResponseRedirect(self.get_success_url())
        self.object = User.objects.get(pk=self.kwargs.get("pk"))
        self.password_form = self.get_password_form()
        self.form = self.get_form()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if self.password_form.is_valid() is True:
            self.password_form = self.custom_form_validation(self.password_form)
            if self.password_form.is_valid() is False:
                return render(request, self.template_name, self.get_context())
            self.password_form.save()
            return HttpResponseRedirect(self.get_success_url())
        else:
            return render(request, self.template_name, self.get_context())

    def get_password_form(self):
        if self.request.method == "POST":
            self.password_form = CustomPasswordChangeForm(self.object, self.request.POST)
        else:
            self.password_form = CustomPasswordChangeForm(self.object)
        return self.password_form

    def get_context(self):
        context = {"object": self.object, "password_form": self.password_form, "form": self.form}
        return context

    def custom_form_validation(self, form):
        form = self.dont_allow_superuser_to_be_changed_from_non_superuser(form)
        return form

    def dont_allow_superuser_to_be_changed_from_non_superuser(self, form):
        instance = form.save(commit=False)
        if instance.is_superuser:
            if not self.request.user.is_superuser:
                form.add_error(None, "Sie haben keine Berechtigung diesen Nutzer zu bearbeiten")
        return form


class ChangeProfilePasswordView(BaseChangePasswordView):
    template_name = "account/user/profile/profile.html"

    def get_form(self):
        self.form = ProfileFormMixin(instance=self.object)
        return self.form

    def get_success_url(self):
        return reverse_lazy("account:user_profile", kwargs={"pk": self.kwargs.get("pk")})


class ChangeUserPasswordView(BaseChangePasswordView):
    template_name = "account/user/edit/edit.html"

    def get_form(self):
        self.form = EditForm(instance=self.object)
        return self.form

    def get_success_url(self):
        return reverse_lazy("account:user_edit", kwargs={"pk": self.kwargs.get("pk")})


class UserActivationView(LoginRequiredMixin, generic.View):
    @transaction.atomic
    def dispatch(self, request, *args, **kwargs):
        if request.method == "POST":
            items = request.POST.getlist("item")
            users = User.objects.filter(id__in=items)
            print(f"he: {users}")
            for user in users:
                user.is_active = True
                user.save()
            return HttpResponseRedirect(reverse_lazy("account:user_list"))


class UserDeactivationView(LoginRequiredMixin, generic.View):
    @transaction.atomic
    def dispatch(self, request, *args, **kwargs):
        if request.method == "POST":
            items = request.POST.getlist("item")
            users = User.objects.filter(id__in=items, is_superuser=False)
            print(f"he: {users}")
            for user in users:
                user.is_active = False
                user.save()
            return HttpResponseRedirect(reverse_lazy("account:user_list"))


class UserDeletionView(LoginRequiredMixin, generic.View):
    @transaction.atomic
    def dispatch(self, request, *args, **kwargs):
        if request.method == "POST":
            items = request.POST.getlist("item")
            profiles = Profile.objects.filter(user_id__in=items, user__is_superuser=False)
            print(f"he: {profiles}")
            profiles.update(removed=True)
            return HttpResponseRedirect(reverse_lazy("account:user_list"))


class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm

    def form_valid(self, form):
        print(f"bob: {self.request.user.id}")
        success_response = super().form_valid(form)
        if self.request.user.is_superuser:
            return success_response
        if self.request.user.id:
            print(f"safe: {not self.request.user.profile.is_admin}")
            if not self.request.user.profile.is_admin:
                form.add_error(None, "Zugriff verweigert")
                logout(self.request)
                return super().form_invalid(form)
        return success_response

    def post(self, request, *args, **kwargs):

        return super().post(request, *args, **kwargs)


class EmailAuthorizationView(LoginRequiredMixin, generic.View):
    def dispatch(self, request, *args, **kwargs):
        if request.method == "POST":
            form = AccountAuthorizationForm(data=request.POST)
            if form.is_valid() is True:
                mapper_url = os.environ.get("mapper_url") + "/api/v1/mapping/submit_account/"
                host_url = os.environ.get("host_url")
                response = requests.post(mapper_url, data={"email": form.data.get("email"), "url": host_url})
                print(f"status --- {response.status_code}")
                print(f"ban --- {response.text}")
                form.save()
                return HttpResponseRedirect(reverse_lazy("account:authorize_mail"))
            else:
                error_msg = ""
                for error_list in form.errors.values():
                    for error in error_list:
                        error_msg += error + "</br>"
                context = {
                    'status': '400', 'error': error_msg
                }
                print(f"error_____: {error_msg}")
                response = HttpResponse(json.dumps(context), content_type='application/json')
                response.status_code = 400
                return response

        if request.method == "GET":
            template_name = "account/authorization/authorization.html"
            return render(request, template_name, {"form": AccountAuthorizationForm()})


class EmailAuthorizationDeleteView(LoginRequiredMixin, generic.View):
    def dispatch(self, request, *args, **kwargs):
        if request.method == "POST":
            items = request.POST.getlist("item")
            authorizations = AccountAuthorization.objects.filter(id__in=items)
            authorizations.delete()
            return HttpResponseRedirect(reverse_lazy("account:authorize_mail"))
