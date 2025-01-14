from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
import redis

# On initialise un client Redis
# Assure-toi d'avoir REDIS_HOST et REDIS_PORT dans tes settings
r = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=0
)

def game_page(request):
    """
    Renvoie la page principale de jeu (HTML).
    """
    return render(request, 'game/game_page.html')


def get_positions(request):
    """
    Récupère la position des deux raquettes (dans Redis) et renvoie un JSON.
    Ex: { "left": 150, "right": 150 }
    """
    left_y = r.get('paddle_left_y')
    if left_y is None:
        left_y = 150  # Valeur par défaut
    else:
        left_y = int(left_y)

    right_y = r.get('paddle_right_y')
    if right_y is None:
        right_y = 150
    else:
        right_y = int(right_y)

    data = {
        'left': left_y,
        'right': right_y
    }
    return JsonResponse(data)


def update_position(request):
    """
    Met à jour la position d'une raquette en fonction d'un POST
    contenant "player" = ('left' ou 'right') et "direction" = ('up' ou 'down').
    Renvoie un JSON confirmant la nouvelle position.
    """
    if request.method == 'POST':
        player = request.POST.get('player')    # 'left' ou 'right'
        direction = request.POST.get('direction')  # 'up' ou 'down'

        # Clé pour Redis : "paddle_left_y" ou "paddle_right_y"
        key = f"paddle_{player}_y"
        current_value = r.get(key)
        if current_value is None:
            current_value = 150
        else:
            current_value = int(current_value)

        # On déplace la raquette de 5 pixels
        step = 5
        if direction == 'up':
            new_value = current_value - step
        else:
            new_value = current_value + step

        # Optionnel : limiter la position pour ne pas sortir du terrain
        # (si le terrain fait 400 px de haut et la raquette 60 px)
        new_value = max(0, min(340, new_value))

        # On stocke la nouvelle valeur en Redis
        r.set(key, new_value)

        return JsonResponse({'status': 'ok', 'new_value': new_value})
    else:
        return JsonResponse({'error': 'Must POST'}, status=400)
