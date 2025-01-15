# game/consumers.py

import json
import redis
from django.conf import settings
from channels.generic.websocket import AsyncWebsocketConsumer

r = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=0
)

class PongConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.game_id = self.scope['url_route']['kwargs']['game_id']
        self.group_name = f"pong_{self.game_id}"

        await self.accept()
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        print(f"[PongConsumer] WebSocket connected for game_id={self.game_id}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        print(f"[PongConsumer] WebSocket disconnected for game_id={self.game_id}")

    async def receive(self, text_data=None, bytes_data=None):
        """
        Reçoit un JSON du type:
        {
          "action": "move",
          "player": "left",  # ou "right"
          "direction": "up"  # ou "down"
        }
        """
        data = json.loads(text_data)
        action = data.get('action')

        if action == 'move':
            player = data['player']
            direction = data['direction']
            await update_paddle_position(self.game_id, player, direction)
            print(f"[PongConsumer] Received move: player={player}, direction={direction} for game_id={self.game_id}")

    async def broadcast_game_state(self, event):
        """
        Reçoit { 'type': 'broadcast_game_state', 'data': { ... } }
        et envoie data au client.
        """
        await self.send(json.dumps(event['data']))
        print(f"[PongConsumer] Broadcast game_state to game_id={self.game_id}")

    async def game_over(self, event):
        """
        Reçoit { 'type': 'game_over', 'winner': 'left' } par ex.
        """
        await self.send(json.dumps({
            'type': 'game_over',
            'winner': event['winner']
        }))
        print(f"[PongConsumer] Broadcast game_over to game_id={self.game_id}, winner={event['winner']}")

async def update_paddle_position(game_id, player, direction):
    """
    Met à jour la position de la raquette dans Redis.
    """
    key = f"{game_id}:paddle_{player}_y"
    current = r.get(key)
    if current is None:
        current = 150
    else:
        current = float(current)

    # Récupérer les effets appliqués au joueur
    inverted = bool(r.get(f"{game_id}:player_{player}_inverted"))
    shrink = r.get(f"{game_id}:player_{player}_paddle_height")
    ice = bool(r.get(f"{game_id}:player_{player}_ice"))
    speed_boost = r.get(f"{game_id}:player_{player}_speed_boost")

    direction_value = 0
    if direction == 'up':
        direction_value = -1
    elif direction == 'down':
        direction_value = 1

    # Appliquer l'inversion des contrôles si nécessaire
    if inverted:
        direction_value = -direction_value

    # Calculer la nouvelle position
    speed = 6  # Vitesse de base
    if speed_boost:
        speed = int(speed_boost)  # Vitesse boostée stockée dans Redis

    velocity = direction_value * speed

    # Appliquer la physique de glace si activée
    if ice:
        acceleration = 0.5
        friction = 0.02
        velocity += direction_value * acceleration
        velocity *= (1 - friction)

    new_y = current + velocity

    # Limites de mouvement
    new_y = max(50, min(350 - (int(shrink) if shrink else 60), new_y))

    # Stocker la nouvelle position dans Redis
    r.set(key, new_y)
