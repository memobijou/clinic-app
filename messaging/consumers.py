from asgiref.sync import async_to_sync
from channels.consumer import AsyncConsumer, SyncConsumer
from channels.generic.websocket import WebsocketConsumer
import json
from channels.db import database_sync_to_async
from django.db.models import Q
from rest_framework.renderers import JSONRenderer
from rest_framework.settings import api_settings
from rest_framework.views import APIView
from messaging.models import TextMessage, ConnectionHistory
from django.core import serializers
from django.core.paginator import Paginator
from urllib import parse
import asyncio
from messaging.serializers import TextMessageSerializer
from rest_framework.response import Response
from messaging.viewsets import text_message_page_size
from rest_framework.authtoken.models import Token
from channels.exceptions import DenyConnection


class ChatConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.receiver_id = self.scope["url_route"]["kwargs"]["receiver"]
        self.sender_id = self.scope["url_route"]["kwargs"]["sender"]

    def connect(self):
        print(f"hello world 1")
        async_to_sync(self.channel_layer.group_add)(
            f"chat-{self.receiver_id}-{self.sender_id}", self.channel_name)
        async_to_sync(self.channel_layer.group_add)(
            f"chat-{self.sender_id}-{self.receiver_id}", self.channel_name)
        print(f"bababaababab: {self.sender_id} - {self.receiver_id} --- {self.channel_name}")
        history = ConnectionHistory.objects.filter(sender_id=self.sender_id, receiver_id=self.receiver_id)
        if history.count() > 1:
            history.update(connected=True)
        else:
            ConnectionHistory.objects.update_or_create(sender_id=self.sender_id, receiver_id=self.receiver_id,
                                                       connected=True)
        self.accept()

    def disconnect(self, close_code):
        # async_to_sync(self.channel_layer.group_add)(
        #     f"chat-{self.receiver_id}-{self.sender_id}", self.channel_name)
        # async_to_sync(self.channel_layer.group_add)(
        #     f"chat-{self.sender_id}-{self.receiver_id}", self.channel_name)
        history = ConnectionHistory.objects.filter(sender_id=self.sender_id, receiver_id=self.receiver_id)
        if history.count() > 1:
            history.update(connected=False)
        else:
            ConnectionHistory.objects.update_or_create(sender_id=self.sender_id, receiver_id=self.receiver_id,
                                                       connected=False)
        print(f"fulya")

    def receive(self, text_data=None, bytes_data=None):
        async_to_sync(self.channel_layer.group_send)(
            f"chat-{self.receiver_id}-{self.sender_id}",
            {
                "type": "websocket.send",
                "text": text_data,
            },
        )
        async_to_sync(self.channel_layer.group_send)(
            f"chat-{self.sender_id}-{self.receiver_id}",
            {
                "type": "websocket.send",
                "text": text_data,
            },
        )

    def websocket_send(self, event):
        self.send(
            text_data=self.get_chat(self.sender_id, self.receiver_id)
        )

    def get_chat(self, sender_id, receiver_id):
        queryset = TextMessage.objects.filter(
                Q(Q(Q(sender__pk=sender_id) & Q(receiver__pk=receiver_id)) |
                  Q(Q(sender__pk=receiver_id) & Q(receiver__pk=sender_id))))
        text_messages = Paginator(queryset, text_message_page_size).page(1)
        serializer = TextMessageSerializer(text_messages, many=True)
        response = Response(serializer.data, content_type="application/json")
        response.accepted_renderer = JSONRenderer()
        response.accepted_media_type = "application/json"
        response.renderer_context = {}
        return response.rendered_content.decode()


class GroupChatConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.group_id = self.scope["url_route"]["kwargs"]["group"]
        self.receiver_id = self.scope["url_route"]["kwargs"]["receiver"]

    def connect(self):
        print(f"hello world 1")
        async_to_sync(self.channel_layer.group_add)(
            f"group-chat-{self.group_id}", self.channel_name)
        print(f"mamamamaba: {self.group_id} --- {self.channel_name}")
        ConnectionHistory.objects.update_or_create(receiver_id=self.receiver_id, group_id=self.group_id,
                                                   connected=True)
        self.accept()

    def disconnect(self, close_code):
        ConnectionHistory.objects.update_or_create(receiver_id=self.receiver_id, group_id=self.group_id,
                                                   connected=False)
        print(f"fulya")

    def receive(self, text_data=None, bytes_data=None):
        async_to_sync(self.channel_layer.group_send)(
            f"group-chat-{self.group_id}",
            {
                "type": "websocket.send",
                "text": text_data,
            },
        )

    def websocket_send(self, event):
        self.send(
            text_data=self.get_chat(self.group_id)
        )

    def get_chat(self, group_id):
        queryset = TextMessage.objects.filter(group_id=group_id)
        text_messages = Paginator(queryset, text_message_page_size).page(1)
        serializer = TextMessageSerializer(text_messages, many=True)
        response = Response(serializer.data, content_type="application/json")
        response.accepted_renderer = JSONRenderer()
        response.accepted_media_type = "application/json"
        response.renderer_context = {}
        return response.rendered_content.decode()


class ChatConsumerOLD(AsyncConsumer):
    async def websocket_connect(self, event):
        print("connected ", event)
        receiver_id = self.scope["url_route"]["kwargs"]["receiver"]
        sender_id = self.scope["url_route"]["kwargs"]["sender"]
        self.channel_layer.group_add("chat-" + str(receiver_id) + "-" + str(sender_id), self.channel_name)
        # self.channel_layer.group_add("chat-" + str(sender_id) + "-" + str(receiver_id), self.channel_name)
        await self.send({
            "type": "websocket.accept",
        })

        # query_string = parse.parse_qs(self.scope.get("query_string").decode("UTF-8"))

    async def websocket_receive(self, event):
        print(f"lol {event}")
        token = event.get("text")
        print(f"baa: {self}")
        if "Token" in token:
            token_name, token_key = token.split()
            if Token.objects.filter(key=token_key).count() == 1:
                print(token_key)

                # while True:
                receiver_id = self.scope["url_route"]["kwargs"]["receiver"]
                sender_id = self.scope["url_route"]["kwargs"]["sender"]
                #  history = ConnectionHistory.objects.filter(sender_id=sender_id, receiver_id=receiver_id)

                ConnectionHistory.objects.update_or_create(sender_id=sender_id, receiver_id=receiver_id,
                                                           connected=True)
                print("waaaaa")
                await asyncio.sleep(0.5)
                await self.channel_layer.group_send(
                    "chat-" + str(receiver_id) + "-" + str(sender_id),
                    {
                        "type": "websocket.send",
                        "text": await self.get_chat(sender_id, receiver_id),
                    })
                # await self.channel_layer.group_send(
                #     "chat-" + str(sender_id) + "-" + str(receiver_id),
                #     {
                #         "type": "websocket.send",
                #         "text": await self.get_chat(sender_id, receiver_id),
                #     })
            else:
                await self.send({
                    "type": "websocket.send",
                    "text": await self.error_message_wrong_token(),
                })
                raise DenyConnection
        # await self.send({
        #     "type": "websocket.send",
        #     "text": event["text"],
        # })

    async def websocket_disconnect(self, close_code):
        print("HÜLSE")
        receiver_id = self.scope["url_route"]["kwargs"]["receiver"]
        sender_id = self.scope["url_route"]["kwargs"]["sender"]
        history = ConnectionHistory.objects.filter(sender_id=sender_id, receiver_id=receiver_id)
        history.update_or_create(connected=False)
        print("disconnected", close_code)

    async def get_chat(self, sender_id, receiver_id):
        queryset = TextMessage.objects.filter(
                Q(Q(Q(sender__pk=sender_id) & Q(receiver__pk=receiver_id)) |
                  Q(Q(sender__pk=receiver_id) & Q(receiver__pk=sender_id))))
        text_messages = Paginator(queryset, text_message_page_size).page(1)
        serializer = TextMessageSerializer(text_messages, many=True)
        response = Response(serializer.data, content_type="application/json")
        response.accepted_renderer = JSONRenderer()
        response.accepted_media_type = "application/json"
        response.renderer_context = {}
        # response_json = json.loads(response.rendered_content.decode())
        return response.rendered_content.decode()
        # # self.scope["url_route"]["kwargs"]["reveiver"]
        # p = Paginator(TextMessage.objects.all(), 10)
        # chat_json = serializers.serialize("json", p.page(1))
        # return chat_json

    async def websocket_send(self, event):
        receiver_id = self.scope["url_route"]["kwargs"]["receiver"]
        sender_id = self.scope["url_route"]["kwargs"]["sender"]
        await self.channel_layer.send(
            {
                "text": "asdsadsadsads",
            }
        )

    async def error_message_wrong_token(self):
        return "Invalid token"
