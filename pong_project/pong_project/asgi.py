# """
# ASGI config for pong_project project.

# It exposes the ASGI callable as a module-level variable named ``application``.

# For more information on this file, see
# https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
# """

# import os

# from django.core.asgi import get_asgi_application

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pong_project.settings')

# application = get_asgi_application()


# import os
# from channels.auth import AuthMiddlewareStack
# from channels.routing import ProtocolTypeRouter, URLRouter
# from django.core.asgi import get_asgi_application
# import game.routing  # fichier où tu définis tes routes websockets

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pong_project.settings')

# django_asgi_app = get_asgi_application()

# application = ProtocolTypeRouter({
#     # Pour les requêtes HTTP classiques
#     "http": django_asgi_app,
#     # Pour les connexions WebSocket
#     "websocket": AuthMiddlewareStack(
#         URLRouter(
#             game.routing.websocket_urlpatterns
#         )
#     ),
# })



# pong_project/asgi.py

import os
import django
import asyncio
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
import game.routing  # fichier où tu définis tes routes websockets

# 1. Récupérer la loop
loop = asyncio.get_event_loop()

# 2. Définir DJANGO_SETTINGS_MODULE
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pong_project.settings')
django.setup()

# 3. Définir la loop globale
from game.manager import set_global_loop
set_global_loop(loop)

# 4. Créer l'application Channels
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    # Pour les requêtes HTTP classiques
    "http": django_asgi_app,
    # Pour les connexions WebSocket
    "websocket": AuthMiddlewareStack(
        URLRouter(
            game.routing.websocket_urlpatterns
        )
    ),
})
