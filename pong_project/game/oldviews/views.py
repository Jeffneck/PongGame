# game/views.py

from django.http import JsonResponse
from .models import GameSession
from django.shortcuts import render
from .models import GameSession, GameResult
import redis
from django.conf import settings

r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)

def index(request):
    """
    Page d'accueil -> bouton pour créer une partie
    """
    return render(request, 'game/index.html')

# @csrf_exempt
def ready_game(request, game_id):
    """
    Marque la partie comme prête à être lancée.
    """
    if request.method == 'POST':
        print(f"[DEBUG] game_id reçu dans la vue : {game_id}")  # Debug
        try:
            game_session = GameSession.objects.get(pk=game_id)
            print(f"[DEBUG] gamesession trouvee : {game_session}")  # Debug
            game_session.status = 'ready'  # On passe le statut à 'ready'
            game_session.save()
            return JsonResponse({'success': True, 'message': 'Game marked as ready'})
        except GameSession.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Game session not found'}, status=404)
    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=400)

def list_results(request):
    """
    Affiche la liste des parties terminées.
    """
    results = GameResult.objects.select_related('game').order_by('-ended_at')[:20]
    return render(request, 'game/list_results.html', {'results': results})
