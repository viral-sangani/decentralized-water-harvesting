from django.urls import path
from channels.routing import ProtocolTypeRouter, URLRouter
from .views import LiveScoreConsumer

websockets = URLRouter([
    path(
        "ws/block-chain/", LiveScoreConsumer,
        name="lock-chain",
    ),
])