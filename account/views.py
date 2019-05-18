from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.
from django.views import View
from abc import ABCMeta, abstractmethod
from account.forms import CustomUserCreationForm, ProfileFormMixin, CustomPasswordChangeForm, EditForm
from account.models import Profile
from django.contrib.auth.models import User


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


class UserActivationView(generic.View):
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


class UserDeactivationView(generic.View):
    @transaction.atomic
    def dispatch(self, request, *args, **kwargs):
        if request.method == "POST":
            items = request.POST.getlist("item")
            users = User.objects.filter(id__in=items)
            print(f"he: {users}")
            for user in users:
                user.is_active = False
                user.save()
            return HttpResponseRedirect(reverse_lazy("account:user_list"))


class UserDeletionView(generic.View):
    @transaction.atomic
    def dispatch(self, request, *args, **kwargs):
        if request.method == "POST":
            items = request.POST.getlist("item")
            profiles = Profile.objects.filter(user_id__in=items, user__is_superuser=False)
            print(f"he: {profiles}")
            profiles.update(removed=True)
            return HttpResponseRedirect(reverse_lazy("account:user_list"))
