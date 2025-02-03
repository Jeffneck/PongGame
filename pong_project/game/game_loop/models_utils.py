# game/game_loop/models_utils.py
from django.apps import apps  # Import retardé pour éviter les conflits d'import
from asgiref.sync import sync_to_async

class GameSessionNotFound(Exception):
    """Exception personnalisée pour le cas où la session n'existe pas."""
    pass

class GameParametersNotFound(Exception):
    """Exception levée lorsqu'aucun GameParameters n'est défini dans la GameSession."""
    pass

async def get_gameSession(game_id):
    # print("get_gamesession")
    GameSession = apps.get_model('game', 'GameSession')
    try:
        session = await sync_to_async(GameSession.objects.get)(pk=game_id)
        return session
    except GameSession.DoesNotExist as e:
        raise GameSessionNotFound(f"La GameSession avec l'ID {game_id} n'existe pas.") from e

async def get_gameSession_status(game_id):
    # print("get_gameSession_status")
    session = await get_gameSession(game_id)
    return session.status

async def is_online_gameSession(game_id):
    # print("is_online_gameSession")
    session = await get_gameSession(game_id)
    return session.is_online

async def set_gameSession_status(game_id, status):
    # print("set_gameSession_status")
    GameSession = apps.get_model('game', 'GameSession')
    try:
        # Précharger player_left et player_right pour éviter des appels ORM en mode lazy
        session = await sync_to_async(
            GameSession.objects.select_related('player_left', 'player_right').get
        )(pk=game_id)
        session.status = status
        await sync_to_async(session.save)()
        return session
    except GameSession.DoesNotExist as e:
        raise GameSessionNotFound(f"La GameSession avec l'ID {game_id} n'existe pas.") from e

async def get_gameSession_parameters(game_id):
    GameSession = apps.get_model('game', 'GameSession')
    try:
        session = await sync_to_async(GameSession.objects.get)(pk=game_id)
        parameters = await sync_to_async(getattr)(session, 'parameters', None)
    except parameters is None:
        raise GameParametersNotFound(f"La GameSession avec l'ID {game_id} n'a pas de paramètres définis.")
    return parameters

async def get_LocalTournament(game_id, phase):
    # print("get_LocalTournament")
    LocalTournament = apps.get_model('game', 'LocalTournament')
    if phase == "semifinal1":
        tournament = await sync_to_async(LocalTournament.objects.filter(semifinal1__id=game_id).first)()
    elif phase == "semifinal2":
        tournament = await sync_to_async(LocalTournament.objects.filter(semifinal2__id=game_id).first)()
    else:
        tournament = await sync_to_async(LocalTournament.objects.filter(final__id=game_id).first)()
    return tournament

async def create_gameResults(game_id, endgame_infos):
    # print("create_gameResults")
    """Crée un GameResult après la fin d'un match."""
    GameSession = apps.get_model('game', 'GameSession')
    GameResult = apps.get_model('game', 'GameResult')

    try:
        print(f"[create_gameResults] Creating GameResult for game {game_id}...")
        session = await get_gameSession(game_id)

        def save_game_result():
            GameResult.objects.create(
                game=session,
                winner=endgame_infos['winner'],
                looser=endgame_infos['looser'],
                score_left=endgame_infos['score_left'],
                score_right=endgame_infos['score_right']
            )

        await sync_to_async(save_game_result, thread_sensitive=True)()
    except GameSession.DoesNotExist as e:
        raise GameSessionNotFound(f"La GameSession avec l'ID {game_id} n'existe pas.") from e
