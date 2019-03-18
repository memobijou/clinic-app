from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class TextMessage(models.Model):
    message = models.TextField()
    sender = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="sender_messages")
    receiver = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="receiver_messages")
    created_datetime = models.DateTimeField(null=True, auto_now=True)

    class Meta:
        ordering = ("created_datetime", )
