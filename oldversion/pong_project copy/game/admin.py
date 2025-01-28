# game/admin.py

from django.contrib import admin
from .models import GameSession, GameResult, GameParameters, GameInvitation

@admin.register(GameSession)
class GameSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'player_left', 'player_right', 'status', 'created_at')

@admin.register(GameResult)
class GameResultAdmin(admin.ModelAdmin):
    list_display = ('game', 'winner', 'score_left', 'score_right', 'ended_at')

@admin.register(GameParameters)
class GameParametersAdmin(admin.ModelAdmin):
    list_display = ('game_session', 'ball_speed', 'paddle_size', 'bonus_enabled', 'obstacles_enabled')

@admin.register(GameInvitation)
class GameInvitationAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user', 'status', 'created_at')
