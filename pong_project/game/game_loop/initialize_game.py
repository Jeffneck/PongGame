# game/game_loop/initialize_game.py

from .redis_utils import set_key
from ..game_objects import Paddle, Ball, PowerUpOrb, Bumper
from .dimensions_utils import get_terrain_rect
import random

FIELD_HEIGHT = 300

#------------- INITIALIZE : CREATE ALL GAME OBJECTS WITH THEIR INITIAL VALUES --------------
# def initialize_game_objects(game_id, parameters):
#     paddle_size = {1: 30, 2: 60, 3: 90}[parameters.paddle_size]
#     paddle_speed = 7  # Peut être ajusté si nécessaire
#     ball_speed_multiplier = parameters.ball_speed

#     # Obtenir les dimensions du terrain
#     terrain_rect = get_terrain_rect(game_id)

#     # Initialiser les raquettes
#     paddle_left = Paddle('left', paddle_size, paddle_speed)
#     paddle_right = Paddle('right', paddle_size, paddle_speed)

#     # initialize_game_objects
#     initial_ball_speed_x = random.choice([-3, 3]) * ball_speed_multiplier
#     initial_ball_speed_y = random.choice([-3, 3]) * ball_speed_multiplier

#     ball = Ball(
#         terrain_rect['left'] + terrain_rect['width'] // 2,
#         terrain_rect['top'] + terrain_rect['height'] // 2,
#         initial_ball_speed_x,
#         initial_ball_speed_y
#     )

#     # Initialiser les power-ups et bumpers
#     powerup_orbs = [
#         PowerUpOrb(game_id, 'invert', terrain_rect, color=(255, 105, 180)),  # Rose pour inverser
#         PowerUpOrb(game_id, 'shrink', terrain_rect, color=(255, 0, 0)),      # Rouge pour rétrécir
#         PowerUpOrb(game_id, 'ice', terrain_rect, color=(0, 255, 255)),       # Cyan pour glace
#         PowerUpOrb(game_id, 'speed', terrain_rect, color=(255, 215, 0)),     # Or pour vitesse
#         PowerUpOrb(game_id, 'flash', terrain_rect, color=(255, 255, 0)),     # Jaune pour flash
#         PowerUpOrb(game_id, 'sticky', terrain_rect, color=(50, 205, 50))     # Vert lime pour collant
#     ]

#     bumpers = []
#     if parameters.obstacles_enabled:
#         bumpers = [Bumper(game_id, terrain_rect) for _ in range(3)]  # Ajuster le nombre si nécessaire

#     return paddle_left, paddle_right, ball, powerup_orbs, bumpers

def initialize_game_objects(game_id, parameters):
    # 1) Taille de paddle
    paddle_size = {1: 30, 2: 60, 3: 90}[parameters.paddle_size]
    paddle_speed = 8  # Ajustable

    # 2) Calcul de la vitesse de balle en fonction de parameters.ball_speed
    #    Au lieu d'utiliser un "multiplier", on définit
    #    directement la vitesse absolue.
    speed_map = {1: 3, 2: 5, 3: 8}
    ball_speed = speed_map[parameters.ball_speed]  # ex: 3, 5 ou 8

    # 3) Création des paddles
    from .dimensions_utils import get_terrain_rect
    terrain_rect = get_terrain_rect(game_id)
    from ..game_objects import Paddle, Ball, PowerUpOrb, Bumper
    
    paddle_left = Paddle('left', paddle_size, paddle_speed)
    paddle_right = Paddle('right', paddle_size, paddle_speed)

    # 4) Balle : direction ±x, ±y
    initial_ball_speed_x = random.choice([-1, 1]) * ball_speed
    initial_ball_speed_y = random.choice([-1, 1]) * ball_speed

    # Centre du terrain
    center_x = terrain_rect['left'] + terrain_rect['width'] // 2
    center_y = terrain_rect['top'] + terrain_rect['height'] // 2

    ball = Ball(center_x, center_y, initial_ball_speed_x, initial_ball_speed_y)

    # 5) Créer powerups & bumpers
    powerup_orbs = [
        PowerUpOrb(game_id, 'invert', terrain_rect, color=(255, 105, 180)),
        PowerUpOrb(game_id, 'shrink', terrain_rect, color=(255, 0, 0)),
        PowerUpOrb(game_id, 'ice', terrain_rect, color=(0, 255, 255)),
        PowerUpOrb(game_id, 'speed', terrain_rect, color=(255, 215, 0)),
        PowerUpOrb(game_id, 'flash', terrain_rect, color=(255, 255, 0)),
        PowerUpOrb(game_id, 'sticky', terrain_rect, color=(50, 205, 50))
    ]
    bumpers = []
    if parameters.obstacles_enabled:
        bumpers = [Bumper(game_id, terrain_rect) for _ in range(3)]

    return paddle_left, paddle_right, ball, powerup_orbs, bumpers

#------------- INITIALIZE : UPDATE REDIS DATABASE WITH OBJECTS VALUES--------------
def initialize_redis(game_id, paddle_left, paddle_right, ball, parameters):
    # Positions initiales des raquettes
    set_key(game_id, "paddle_left_y", paddle_left.y)
    set_key(game_id, "paddle_right_y", paddle_right.y)

    # Vélocités initiales des raquettes (0 => immobiles)
    set_key(game_id, "paddle_left_velocity", 0)
    set_key(game_id, "paddle_right_velocity", 0)

    # Store initial paddle heights from parameters / added
    initial_height = {1: 60, 2: 80, 3: 100}[parameters.paddle_size]
    set_key(game_id, "initial_paddle_height", initial_height)
    set_key(game_id, "paddle_left_height", initial_height)
    set_key(game_id, "paddle_right_height", initial_height)

    # Balle
    set_key(game_id, "ball_x", ball.x)
    set_key(game_id, "ball_y", ball.y)
    set_key(game_id, "ball_vx", ball.speed_x)
    set_key(game_id, "ball_vy", ball.speed_y)

    # Store initial ball speed multiplier from parameters / added
    initial_speed = {1: 3, 2: 5, 3: 8}[parameters.ball_speed]
    set_key(game_id, "initial_ball_speed_multiplier", initial_speed)