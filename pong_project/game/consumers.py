# game/consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
import json
import redis
from django.conf import settings

# Client Redis direct (pour stocker la position)
r = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=0
)

class PongConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        # Autoriser la connexion
        await self.accept()
        # Joindre un groupe, pour diffuser à tous
        self.group_name = 'pong_room'
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        # Envoyer les positions initiales
        await self.send_positions()

    async def disconnect(self, close_code):
        # Quitter le groupe
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        """
        On attend un JSON du type :
        {
          "action": "move",
          "player": "left",   # ou "right"
          "direction": "up"   # ou "down"
        }
        """
        data = json.loads(text_data)
        action = data.get("action")

        if action == "move":
            player = data.get("player")
            direction = data.get("direction")
            self.update_paddle_position(player, direction)

            # Diffuser la nouvelle position à tous
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "broadcast_positions"
                }
            )

    def update_paddle_position(self, player, direction):
        key = f"paddle_{player}_y"  # "paddle_left_y" ou "paddle_right_y"
        current_value = r.get(key)
        if current_value is None:
            current_value = 150
        else:
            current_value = int(current_value)

        step = 5
        if direction == 'up':
            new_value = current_value - step
        else:
            new_value = current_value + step

        # on peut limiter la position pour ne pas sortir du terrain
        new_value = max(0, min(340, new_value))  # ex. 0 à 340 si terrain=400, paddle=60

        r.set(key, new_value)

    async def send_positions(self):
        """Récupérer la position en Redis, l'envoyer au client actuel."""
        left_y = r.get('paddle_left_y')
        right_y = r.get('paddle_right_y')
        if left_y is None:
            left_y = 150
        else:
            left_y = int(left_y)
        if right_y is None:
            right_y = 150
        else:
            right_y = int(right_y)

        data = {
            "type": "positions",
            "left": left_y,
            "right": right_y
        }
        await self.send(text_data=json.dumps(data))

    async def broadcast_positions(self, event):
        """
        Méthode appelée quand on fait un "group_send" avec "type": "broadcast_positions".
        On envoie la position à tous les clients du groupe.
        """
        await self.send_positions()
