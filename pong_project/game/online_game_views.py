# game/views.py

# from django.shortcuts import render,  redirect
# from .models import GameSession
# from .manager import schedule_game
# from .forms import GameParametersForm


# def parameter_online_game(request):
#     """
#     Crée un GameSession (UUID), init Redis avec les paramètres personnalisés, lance la loop en non-bloquant
#     """
#     if request.method == 'POST':
#         form = GameParametersForm(request.POST)
#         if form.is_valid():
#             # Créer une nouvelle GameSession
#             session = GameSession.objects.create(status='waiting') 
#             game_id = str(session.id)

#             # Créer les GameParameters liés à cette session
#             parameters = form.save(commit=False)
#             parameters.game_session = session
#             parameters.save()
#             print(f"[create_game] GameSession {game_id} created avec paramètres personnalisés. Scheduling game_loop.")
#             schedule_game(game_id)

#             return redirect('send_online_game_invitation', game_id=game_id)
#     else:
#         form = GameParametersForm()
#     return render(request, 'online_game/parameter_online_game.html', {'form': form})


# def live_local_game(request, game_id):
#     """
#     Affiche la page HTML (canvas + websocket) pour la partie <game_id>
#     """
#     return render(request, 'game/local_game/live_local_game.html', {'game_id': game_id})
