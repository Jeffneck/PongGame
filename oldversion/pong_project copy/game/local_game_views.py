# local_game_views.py

from django.shortcuts import render,  redirect
from .models import GameSession
from .manager import schedule_game
from .forms import GameParametersForm
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def parameter_local_game(request):
    """
    Crée un GameSession (UUID), init Redis avec les paramètres personnalisés, lance la loop en non-bloquant
    """
    if request.method == 'POST':
        form = GameParametersForm(request.POST)
        if form.is_valid():
            # Créer une nouvelle GameSession avec des joueurs par défaut
            session = GameSession.objects.create(
                status='waiting',
                player_left='Player_left',
                player_right='Player_right'
            )
            game_id = str(session.id)

            # Créer les GameParameters liés à cette session
            parameters = form.save(commit=False)
            parameters.game_session = session
            parameters.save()
            print(f"[parameter_local_game] GameSession {game_id} created avec paramètres personnalisés. Scheduling game_loop.")
            schedule_game(game_id)

            return redirect('live_local_game', game_id=game_id)
    else:
        form = GameParametersForm()
    return render(request, 'game/local_game/parameter_local_game.html', {'form': form})

def live_local_game(request, game_id):
    """
    Affiche la page HTML (canvas + websocket) pour la partie <game_id>
    """
    return render(request, 'game/local_game/live_local_game.html', {'game_id': game_id})
