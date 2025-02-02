# game/game_loop/models_utils.py
from django.apps import apps  # Import retardé pour éviter les conflits d'import
from asgiref.sync import sync_to_async


async def get_gameSession_status(game_id):
    GameSession = apps.get_model('game', 'GameSession')
    try:
        session = await sync_to_async(GameSession.objects.get)(pk=game_id)
        return session.status
    except GameSession.DoesNotExist:
        return 'finished'

async def is_gameSession_Online(game_id):
    GameSession = apps.get_model('game', 'GameSession')
    try:
        session = await sync_to_async(GameSession.objects.get)(pk=game_id)
        return session.is_online
    except GameSession.DoesNotExist:
        return False

async def set_gameSession_status(game_id, status):
    GameSession = apps.get_model('game', 'GameSession')
    try:
        # Précharger player_left et player_right pour éviter des appels ORM en mode lazy
        session = await sync_to_async(
            GameSession.objects.select_related('player_left', 'player_right').get
        )(pk=game_id)
        session.status = status
        await sync_to_async(session.save)()
        return session
    except GameSession.DoesNotExist:
        return None



async def get_gameSession_parameters(game_id):
    GameSession = apps.get_model('game', 'GameSession')
    try:
        session = await sync_to_async(GameSession.objects.get)(pk=game_id)
        parameters = await sync_to_async(getattr)(session, 'parameters', None)
        return parameters
    except GameSession.DoesNotExist:
        return None
    
async def get_LocalTournament(game_id, phase):
    LocalTournament = apps.get_model('game', 'LocalTournament')
    if phase == "semifinal1":
        tournament = await sync_to_async(LocalTournament.objects.filter(semifinal1__id=game_id).first)()
    elif phase == "semifinal2":
        tournament = await sync_to_async(LocalTournament.objects.filter(semifinal2__id=game_id).first)()
    else:
        tournament = await sync_to_async(LocalTournament.objects.filter(final__id=game_id).first)()
    return tournament


# async def create_gameResults(game_id, endgame_infos):
#     GameSession = apps.get_model('game', 'GameSession')
#     GameResult = apps.get_model('game', 'GameResult')
#     try:
#         session = await sync_to_async(GameSession.objects.get)(pk=game_id)
#         await sync_to_async(GameResult.objects.create)(
#             game=session,
#             winner=endgame_infos['winner'],
#             looser=endgame_infos['looser'],
#             score_left=endgame_infos['score_left'],
#             score_right=endgame_infos['score_right']
#         )
#     except GameSession.DoesNotExist:
#         print(f"[create_gameResults] GameSession {game_id} does not exist.")

async def create_gameResults(game_id, endgame_infos):
    """Crée un GameResult après la fin d'un match."""
    GameSession = apps.get_model('game', 'GameSession')
    GameResult = apps.get_model('game', 'GameResult')

    try:
        print(f"[create_gameResults] Creating GameResult for game {game_id}...")
        # Récupérer la session de jeu en mode async
        session = await sync_to_async(GameSession.objects.get)(pk=game_id)

        # ✅ Regrouper la création de GameResult dans une fonction synchrone
        def save_game_result():
            GameResult.objects.create(
                game=session,
                winner=endgame_infos['winner'],
                looser=endgame_infos['looser'],
                score_left=endgame_infos['score_left'],
                score_right=endgame_infos['score_right']
            )

        # ✅ Exécuter la sauvegarde dans un thread synchrone sécurisé
        await sync_to_async(save_game_result, thread_sensitive=True)()

    except GameSession.DoesNotExist:
        print(f"[create_gameResults] GameSession {game_id} does not exist.")
    except Exception as e:
        print(f"[create_gameResults] Error creating GameResult: {e}")