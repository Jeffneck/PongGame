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


import os
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import game.routing  # fichier où tu définis tes routes websockets

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pong_project.settings')

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
