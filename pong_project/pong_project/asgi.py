# pong_project/asgi.py

import os
import django
import asyncio
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from game.manager import set_global_loop
import game.routing  # Assure-toi que ce chemin est correct

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pong_project.settings')
django.setup()

# Définir le gestionnaire de lifespan
class LifespanHandler:
    async def __call__(self, scope, receive, send):
        if scope['type'] != 'lifespan':
            return

        while True:
            event = await receive()
            if event['type'] == 'lifespan.startup':
                # Récupérer l'event loop en cours
                loop = asyncio.get_running_loop()
                set_global_loop(loop)
                print("[LifespanHandler] Event loop set as global loop.")
                await send({'type': 'lifespan.startup.complete'})
            elif event['type'] == 'lifespan.shutdown':
                await send({'type': 'lifespan.shutdown.complete'})
                break

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            game.routing.websocket_urlpatterns
        )
    ),
    "lifespan": LifespanHandler(),
})
