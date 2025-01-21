# game/game_loop/dimensions_utils.py
def get_terrain_rect(game_id):
    """
    Retourne les dimensions du terrain. Peut être ajusté pour récupérer les dimensions dynamiquement.
    """
    return {
        'left': 50,
        'top': 50,
        'width': 700,
        'height': 300
    }
