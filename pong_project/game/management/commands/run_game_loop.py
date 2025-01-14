# game/management/commands/run_game_loop.py
import asyncio
from django.core.management.base import BaseCommand
from game.game_loop import game_loop

class Command(BaseCommand):
    help = 'Run the Pong game loop'

    def handle(self, *args, **options):
        asyncio.run(game_loop())
