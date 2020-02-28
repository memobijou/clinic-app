from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from channels.auth import AuthMiddlewareStack
from django.urls import path
from messaging.consumers import ChatConsumer
from uniklinik.channels_auth import TokenAuthMiddlewareStack

application = ProtocolTypeRouter({
    "websocket":
    # Empty for now (http->django views is added by default)
    AllowedHostsOriginValidator(
        TokenAuthMiddlewareStack(
            URLRouter([
                path('messaging/chat/<int:receiver>/<int:sender>/', ChatConsumer)
            ])
        )
    )
})
