# game/game_loop/game_session_utils.py
from ..models import GameSession, GameParameters, GameResult

from asgiref.sync import sync_to_async

async def get_gameSession_status(game_id):
    try:
        session = await sync_to_async(GameSession.objects.get)(pk=game_id)
        return session.status
    except GameSession.DoesNotExist:
        return 'finished'

async def set_gameSession_finished(game_id):
    session = await sync_to_async(GameSession.objects.get)(pk=game_id)
    return session.status = "finished"

async def get_game_parameters(game_id):
    try:
        session = await sync_to_async(GameSession.objects.get)(pk=game_id)
        parameters = await sync_to_async(getattr)(session, 'parameters', None)
        return parameters
    except GameSession.DoesNotExist:
        return None
    
#toute les fonctions qui accedent ou modifient les models enregistres


# Ajoutez d'autres fonctions nécessaires, en important depuis les modules respectifs.
