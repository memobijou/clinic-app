from asgiref.sync import async_to_sync
from django.db import models
from django.contrib.auth.models import User
# Create your models here.
from channels.layers import get_channel_layer


class TextMessage(models.Model):
    message = models.TextField()
    sender = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="sender_messages")
    receiver = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="receiver_messages")
    created_datetime = models.DateTimeField(null=True, auto_now=True)
    group = models.ForeignKey(to="account.Group", null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ("-created_datetime", )

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        channel_layer = get_channel_layer()

        if self.receiver_id is not None and self.group_id is None:
            async_to_sync(channel_layer.group_send)(f"chat-{self.receiver_id}-{self.sender_id}",
                                                    {"type": "websocket.send"})
            async_to_sync(channel_layer.group_send)(f"chat-{self.sender_id}-{self.receiver_id}",
                                                    {"type": "websocket.send"})

        if self.receiver_id is None and self.group_id is not None:
            async_to_sync(channel_layer.group_send)(f"group-chat-{self.group_id}", {"type": "websocket.send"})
        return super().save(force_insert=False, force_update=False, using=None, update_fields=None)


class ConnectionHistory(models.Model):
    sender = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="sender_histories")
    receiver = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="receiver_histories")
    group = models.ForeignKey("account.Group", null=True, on_delete=models.SET_NULL)
    connected = models.BooleanField(default=False)
    channel_name = models.CharField(max_length=400, null=True, blank=True)
