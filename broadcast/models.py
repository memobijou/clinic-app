from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Broadcast(models.Model):
    class Meta:
        ordering = ("-send_datetime", )

    text = models.TextField()
    sender = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="broadcasts")
    send_datetime = models.DateTimeField(null=True, auto_now=True)


class Like(models.Model):
    class Meta:
        ordering = ("-like_datetime", )

    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="likes")
    broadcast = models.ForeignKey("broadcast.Broadcast", null=True, on_delete=models.SET_NULL)
    like_datetime = models.DateTimeField(null=True, auto_now=True)


class Comment(models.Model):
    class Meta:
        ordering = ("-send_datetime", )

    text = models.TextField()
    sender = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="comments")
    send_datetime = models.DateTimeField(null=True, auto_now=True)
    broadcast = models.ForeignKey("broadcast.Broadcast", null=True, on_delete=models.SET_NULL)
