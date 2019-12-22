from channels.routing import ProtocolTypeRouter, URLRouter
from blockchain.routing import websockets

application = ProtocolTypeRouter({
    "websocket": websockets,
})