from django.db import models
from django.contrib.auth.models import User
# Create your models here.


def get_name(self):
    return f"{self.first_name or ''} {self.last_name or ''}"

User.add_to_class("__str__", get_name)
