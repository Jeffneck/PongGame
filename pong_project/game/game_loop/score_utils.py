# game/game_loop/score_utils.py

from channels.layers import get_channel_layer
from asgiref.sync import sync_to_async
from .broadcast import notify_game_finished, notify_powerup_expired, notify_bumper_expired
from .redis_utils import set_key, get_key, scan_and_delete_keys, delete_key
from .models_utils import is_online_gameSession, set_gameSession_status, create_gameResults, get_LocalTournament

from .powerups_utils import handle_powerups_spawn, delete_powerup_redis
from .bumpers_utils import handle_bumpers_spawn, delete_bumper_redis
# transformer en parametre ajustable GameParameters?
WIN_SCORE = 6 


async def reset_all_objects(game_id, powerup_orbs, bumpers): # / added
    """Reset all active powerups and bumpers when a point is scored."""
    # Reset all powerups
    for powerup in powerup_orbs:
        if powerup.active:
            delete_powerup_redis(game_id, powerup)
            powerup.deactivate()
            await notify_powerup_expired(game_id, powerup)

    # Reset all bumpers
    for bumper in bumpers:
        if bumper.active:
            delete_bumper_redis(game_id, bumper)
            bumper.deactivate()
            await notify_bumper_expired(game_id, bumper)

    # Reset any active effects
    keys_to_delete = [
        "paddle_left_sticky", "paddle_right_sticky",
        "paddle_left_inverted", "paddle_right_inverted",
        "paddle_left_ice_effect", "paddle_right_ice_effect",
        "paddle_left_speed_boost", "paddle_right_speed_boost",
        "flash_effect"
    ]
    for key in keys_to_delete:
        delete_key(game_id, key)

    # Reset paddle heights to initial values
    initial_height = float(get_key(game_id, "initial_paddle_height"))
    set_key(game_id, "paddle_left_height", initial_height)
    set_key(game_id, "paddle_right_height", initial_height)


def handle_score(game_id, scorer):
    if scorer == 'score_left':
        score_left = int(get_key(game_id, "score_left") or 0) + 1
        set_key(game_id, "score_left", score_left)
        print(f"[loop.py] Player Left scored. Score: {score_left} - {get_key(game_id, 'score_right')}")            

    else :
        score_right = int(get_key(game_id, "score_right") or 0) + 1
        set_key(game_id, "score_right", score_right)
        print(f"[loop.py] Player Right scored. Score: {get_key(game_id, 'score_left')} - {score_right}")



def winner_detected(game_id):

    score_left = int(get_key(game_id, "score_left") or 0)
    score_right = int(get_key(game_id, "score_right") or 0)

    if (score_left == WIN_SCORE or score_right == WIN_SCORE):
        return True
    return False

async def finish_game(game_id):
    # Récupérer les scores depuis Redis
    score_left = int(get_key(game_id, "score_left") or 0)
    score_right = int(get_key(game_id, "score_right") or 0)

    # Marquer la session comme terminée et récupérer ses informations
    gameSession = await set_gameSession_status(game_id, "finished")
    if not gameSession:
        print(f"[finish_game] GameSession {game_id} does not exist.")
        return

    # Pour être sûr que les attributs player_left et player_right sont préchargés,
    # vérifiez qu'ils ne déclenchent pas de requête additionnelle.
    # Ici, ils ont été chargés grâce au select_related dans set_gameSession_status.

    # Si la GameSession est Online, créer un enregistrement des gameResults
    if score_left > score_right:
        winner = gameSession.player_left
        winner_local = gameSession.player_left_local
        looser = gameSession.player_right
        looser_local = gameSession.player_right_local
    else:
        winner = gameSession.player_right
        winner_local  = gameSession.player_right_local
        looser = gameSession.player_left
        looser_local = gameSession.player_left_local

    endgame_infos = {
        'winner': winner,
        'looser': looser,
        'winner_local': winner_local,
        'looser_local': looser_local,
        'score_left': score_left,
        'score_right': score_right,
    }
    gameSession_isOnline = await is_online_gameSession(game_id)
    await create_gameResults(game_id, gameSession_isOnline, endgame_infos)

    # Gestion du tournoi (inchangé)
    tournament = await get_LocalTournament(game_id, "semifinal1")
    if tournament:
        print(f"[finish_game] this game was semifinal1 from tournament game_id={game_id}")
        tournament.status = 'semifinal1_done'
        tournament.winner_semifinal_1 = winner_local
        await sync_to_async(tournament.save)()
    else:
        tournament = await get_LocalTournament(game_id, "semifinal2")
        if tournament:
            tournament.status = 'semifinal2_done'
            tournament.winner_semifinal_2 = winner_local
            await sync_to_async(tournament.save)()
        else:
            tournament = await get_LocalTournament(game_id, "final")
            if tournament:
                tournament.status = 'finished'
                tournament.winner_final = winner_local
                await sync_to_async(tournament.save)()
            else:
                print(f"[finish_game] No tournament found for game_id={game_id}")

    tournament_id = gameSession.tournament_id
    print(f"[finish_game] tournament_id={tournament_id}")
    if gameSession_isOnline:
        await notify_game_finished(game_id, tournament_id, winner, looser)
    else :
        await notify_game_finished(game_id, tournament_id, winner_local, looser_local)

    scan_and_delete_keys(game_id)
    print(f"[loop.py] Redis keys deleted for game_id={game_id}")
