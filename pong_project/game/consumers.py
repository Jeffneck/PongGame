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
            update_paddle(self.game_id, player, direction)
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

def update_paddle(game_id, player, direction):
    """
    Met à jour la position de la raquette dans Redis.
    """
    # Ex: paddle_left_y => f"{game_id}:paddle_left_y"
    key = f"{game_id}:paddle_{player}_y"
    current = r.get(key)
    if current is None:
        current = 150
    else:
        current = float(current)
    step = 5
    if direction == 'up':
        current -= step
    else:
        current += step
    # Limites
    current = max(0, min(340, current))
    r.set(key, current)
    print(f"[update_paddle] Updated {key} to {current}")
