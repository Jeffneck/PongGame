# game/consumers.py

import json
import redis
from django.conf import settings
from channels.generic.websocket import AsyncWebsocketConsumer

from .game_loop.redis_utils import get_key

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
        data = json.loads(text_data)
        action = data.get('action')
        player = data.get('player')

        if action == 'start_move':
            direction = data.get('direction')  # 'up' ou 'down'
            self.start_move_paddle(player, direction)

        elif action == 'stop_move':
            self.stop_move_paddle(player)

    def start_move_paddle(self, player, direction):
        velocity = 0
        if direction == 'up':
            velocity = -8  # Ajustez la vitesse selon vos préférences
        elif direction == 'down':
            velocity = 8

        r.set(f"{self.game_id}:paddle_{player}_velocity", velocity)
        print(f"[PongConsumer] start_move_paddle: player={player}, velocity={velocity}")

    def stop_move_paddle(self, player):
        r.set(f"{self.game_id}:paddle_{player}_velocity", 0)
        print(f"[PongConsumer] stop_move_paddle: player={player}")

    # Handlers pour les événements du groupe
    async def broadcast_game_state(self, event):
        await self.send(json.dumps(event['data']))
        # print(f"[PongConsumer] Broadcast game_state for game_id={self.game_id}")

    async def game_over(self, event):
        await self.send(json.dumps({
            'type': 'game_over',
            'winner': event['winner'],
            'looser': event.get('looser', None),
        }))
        print(f"[PongConsumer] Broadcast game_over for game_id={self.game_id}")

    async def powerup_applied(self, event):
        await self.send(json.dumps({
            'type': 'powerup_applied',
            'player': event['player'],
            'effect': event['effect'],
            'duration': event['duration']
        }))
        print(f"[PongConsumer] Broadcast powerup_applied for game_id={self.game_id}, player={event['player']}, effect={event['effect']}, duration={event['duration']}")

    async def powerup_spawned(self, event):
        await self.send(json.dumps({
            'type': 'powerup_spawned',
            'powerup': event['powerup']
        }))
        print(f"[PongConsumer] Broadcast powerup_spawned for game_id={self.game_id}")

    async def powerup_expired(self, event):
        await self.send(json.dumps({
            'type': 'powerup_expired',
            'powerup': event['powerup']
        }))
        print(f"[PongConsumer] Broadcast powerup_expired for game_id={self.game_id}")

    async def bumper_spawned(self, event):
        await self.send(json.dumps({
            'type': 'bumper_spawned',
            'bumper': event['bumper']
        }))
        print(f"[PongConsumer] Broadcast bumper_spawned for game_id={self.game_id}")

    async def bumper_expired(self, event):
        await self.send(json.dumps({
            'type': 'bumper_expired',
            'bumper': event['bumper']
        }))
        print(f"[PongConsumer] Broadcast bumper_expired for game_id={self.game_id}")

    async def collision_event(self, event):
        await self.send(json.dumps({
            'type': 'collision_event',
            'collision': event['collision']
        }))
        print(f"[PongConsumer] Broadcast collision_event for game_id={self.game_id}")


# [IMPROVE] adapter le consummer  aux notifications envoyees par broadcast.py