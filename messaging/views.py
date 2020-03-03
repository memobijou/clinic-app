from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.http import HttpResponse
from django.shortcuts import render


def alarm(request):
    receiver_id = 1
    sender_id = 2
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(f"chat-{receiver_id}-{sender_id}", {"type": "websocket.send"})
    async_to_sync(channel_layer.group_send)(f"chat-{sender_id}-{receiver_id}", {"type": "websocket.send"})
    return HttpResponse('<p>Done</p>')
