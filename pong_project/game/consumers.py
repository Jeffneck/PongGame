# game/consumers.py
import json
import redis
from django.conf import settings
from channels.generic.websocket import AsyncWebsocketConsumer

r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)

class PongConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add('pong_room', self.channel_name)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard('pong_room', self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')
        if action == 'move':
            self.update_paddle(data['player'], data['direction'])

    def update_paddle(self, player, direction):
        key = f'paddle_{player}_y'
        current_val = r.get(key)
        if current_val is None:
            current_val = 150
        else:
            current_val = float(current_val)

        step = 5
        if direction == 'up':
            current_val -= step
        else:
            current_val += step

        # Limites
        current_val = max(0, min(340, current_val))

        r.set(key, current_val)

    # Reçoit le "group_send" => envoie au client
    async def broadcast_game_state(self, event):
        await self.send(json.dumps(event['data']))
