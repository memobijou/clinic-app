from channels.consumer import AsyncConsumer
import json
from channels.db import database_sync_to_async
from rest_framework.renderers import JSONRenderer
from rest_framework.settings import api_settings
from rest_framework.views import APIView
from messaging.models import TextMessage
from django.core import serializers
from django.core.paginator import Paginator
from urllib import parse
import asyncio
from messaging.serializers import TextMessageSerializer
from rest_framework.response import Response

from messaging.viewsets import text_message_page_size


class ChatConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        print("connected ", event)
        receiver_id = self.scope["url_route"]["kwargs"]["receiver"]
        sender_id = self.scope["url_route"]["kwargs"]["sender"]

        await self.send({
            "type": "websocket.accept",
        })

        # print("+++++++ " + str(self.get_chat()))
        # query_string = parse.parse_qs(self.scope.get("query_string").decode("UTF-8"))

        while True:
            await asyncio.sleep(1)
            await self.send({
                "type": "websocket.send",
                "text": await self.get_chat(sender_id, receiver_id),
            })

    async def websocket_receive(self, event):
        await self.send({
            "type": "websocket.send",
            "text": event["text"],
        })

    async def websocket_disconnect(self, event):
        print("disconnected", event)

    async def get_chat(self, sender_id, receiver_id):
        text_messages = Paginator(TextMessage.objects.filter(sender_id=sender_id, receiver_id=receiver_id),
                                  text_message_page_size).page(1)
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
