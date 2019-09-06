from django.db.models import Q
from rest_framework.authtoken.views import ObtainAuthToken
from django.contrib.auth import authenticate
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import backends
from rest_framework import serializers
from django.contrib.auth.models import User


class CustomModelBackend(backends.ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)
        try:
            user = User.objects.get(Q(username__iexact=username) | Q(email__iexact=username))
        except User.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            User().set_password(password)
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        return super().authenticate(request, username, password, **kwargs)


class CustomAuthToken(ObtainAuthToken):
    pass
