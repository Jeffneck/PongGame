# game/game_loop/redis_utils.py

import redis
from django.conf import settings

r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)

def set_key(game_id, key, value):
    r.set(f"{game_id}:{key}", value)

def get_key(game_id, key):
    return r.get(f"{game_id}:{key}")

def delete_key(game_id, key):
    r.delete(f"{game_id}:{key}")

def scan_and_delete_keys(game_id):
    keys = list(r.scan_iter(f"{game_id}:*"))
    for key in keys:
        r.delete(key)

