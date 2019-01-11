from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import HttpResponseRedirect
from django.urls import reverse_lazy


class HomeView(View):
    def dispatch(self, request, *args, **kwargs):
        # When no User exists, redirects to create first Admin user
        if User.objects.all().count() == 0:
            return HttpResponseRedirect(reverse_lazy("account:create_user"))
        return super().dispatch(request, *args, **kwargs)
