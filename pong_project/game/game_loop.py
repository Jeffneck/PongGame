# game/game_loop.py

import redis
import asyncio
from django.conf import settings
from channels.layers import get_channel_layer
from .models import GameSession, GameResult, GameParameters
from .game_objects import Paddle, Ball, PowerUpOrb, Bumper
from asgiref.sync import sync_to_async
import math
import random
import time

r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)

FIELD_WIDTH = 800
FIELD_HEIGHT = 400
WIN_SCORE = 4

# collision avec les bumpers
COOLDOWN_TIME = 0.5  # Temps en secondes

# Initialize paddles and ball
async def initialize_game_objects(game_id, parameters):
    paddle_size = {1: 30, 2: 60, 3: 90}[parameters.racket_size]
    paddle_speed = 6  # Can be made adjustable if needed
    ball_speed_multiplier = parameters.ball_speed

    # Obtenir les dimensions du terrain
    terrain_rect = await get_terrain_rect(game_id)

    # Initialize paddles
    paddle_left = Paddle('left', paddle_size, paddle_speed)
    paddle_right = Paddle('right', paddle_size, paddle_speed)

    # Initialize ball
    initial_ball_speed_x = 4 * ball_speed_multiplier
    initial_ball_speed_y = 4 * ball_speed_multiplier
    ball = Ball(
        terrain_rect['left'] + terrain_rect['width'] // 2,
        terrain_rect['top'] + terrain_rect['height'] // 2,
        initial_ball_speed_x,
        initial_ball_speed_y
    )

    # Initialize power-ups and bumpers
    powerup_orbs = [
        PowerUpOrb(game_id, 'invert', terrain_rect, color=(255, 105, 180)),  # Pink for invert
        PowerUpOrb(game_id, 'shrink', terrain_rect, color=(255, 0, 0)),      # Red for shrink
        PowerUpOrb(game_id, 'ice', terrain_rect, color=(0, 255, 255)),       # Cyan for ice
        PowerUpOrb(game_id, 'speed', terrain_rect, color=(255, 215, 0)),     # Gold for speed
        PowerUpOrb(game_id, 'flash', terrain_rect, color=(255, 255, 0)),     # Yellow for flash
        PowerUpOrb(game_id, 'sticky', terrain_rect, color=(50, 205, 50))     # Lime green for sticky
    ]

    bumpers = []
    if parameters.bumpers_activation:
        bumpers = [Bumper(game_id, terrain_rect) for _ in range(3)]  # Adjust number as needed

    return paddle_left, paddle_right, ball, powerup_orbs, bumpers

async def get_terrain_rect(game_id):
    """
    Retourne les dimensions du terrain. Peut être ajusté pour récupérer les dimensions dynamiquement.
    """
    return {
        'left': 50,
        'top': 50,
        'width': 700,
        'height': 300
    }

async def game_loop(game_id):
    """
    Boucle principale pour UNE partie identifiée par game_id.
    Tourne ~60 fois/s tant que la partie est "running".
    """
    channel_layer = get_channel_layer()
    dt = 1/60
    print(f"[game_loop.py] Starting loop for game_id={game_id}.")

    try:
        # Récupérer les paramètres du jeu
        parameters = await get_game_parameters(game_id)
        if not parameters:
            print(f"[game_loop.py] No parameters found for game_id={game_id}. Using defaults.")
            parameters = await sync_to_async(GameParameters.objects.create)(
                game_session=await sync_to_async(GameSession.objects.get)(pk=game_id)
            )
        
        # Initialiser les objets de jeu
        paddle_left, paddle_right, ball, powerup_orbs, bumpers = await initialize_game_objects(game_id, parameters)
        print(f"[game_loop.py] Game objects initialized for game_id={game_id}.")
        
        # Initialiser les positions et vélocités dans Redis
        await initialize_redis(game_id, paddle_left, paddle_right, ball, powerup_orbs, bumpers)
        print(f"[game_loop.py] Game objects positions initialized in Redis for game_id={game_id}.")
        
        last_powerup_spawn_time = time.time()
        powerup_spawn_interval = 10  # Adjust as needed

        last_bumper_spawn_time = time.time()
        bumper_spawn_interval = 15  # Adjust as needed

        while True:
            current_time = time.time()
            # print(f"[game_loop.py] game_id={game_id} - Loop iteration at {current_time}")

            # Vérifier si la partie est encore "running"
            session_status = await get_game_status(game_id)
            # print(f"[game_loop.py] game_id={game_id} - Session status: {session_status}")
            if session_status != 'running':
                print(f"[game_loop.py] game_id={game_id} is not running (status={session_status}), breaking loop.")
                break

            # 1. Mettre à jour les positions des raquettes depuis Redis en fonction de la vélocité
            await update_paddles_from_redis(game_id, paddle_left, paddle_right)
            # print(f"[game_loop.py] game_id={game_id} - Paddles positions updated from Redis.")
            # check if ball is stuck to any paddle
            # In game_loop.py, replace the ball movement section in the game loop with:

            # check if ball is stuck to any paddle
            left_stuck = r.get(f"{game_id}:ball_stuck_to_left")
            right_stuck = r.get(f"{game_id}:ball_stuck_to_right")
            ball_moved = False

            left_stuck = r.get(f"{game_id}:ball_stuck_to_left")
            right_stuck = r.get(f"{game_id}:ball_stuck_to_right")
            ball_moved = False

            if left_stuck or right_stuck:
                stuck_side = 'left' if left_stuck else 'right'
                sticky_start = float(r.get(f"{game_id}:sticky_start_{stuck_side}") or 0)
                relative_pos = float(r.get(f"{game_id}:sticky_relative_pos_{stuck_side}") or 0)
                current_paddle = paddle_left if stuck_side == 'left' else paddle_right
                
                # Check if 1 second has passed
                if time.time() - sticky_start >= 1.0:
                    # Get the original speed that was stored when the ball got stuck
                    original_speed_x = float(r.get(f"{game_id}:ball_original_speed_x") or ball.speed_x)
                    original_speed_y = float(r.get(f"{game_id}:ball_original_speed_y") or ball.speed_y)
                    
                    # Calculate the original speed magnitude and boost it
                    original_speed = math.hypot(original_speed_x, original_speed_y)
                    new_speed = original_speed * 1.3
                    
                    # Position the ball and set its velocity
                    if stuck_side == 'left':
                        ball.x = paddle_left.x + paddle_left.width + ball.size
                        ball.speed_x = new_speed  # Move right
                    else:
                        ball.x = paddle_right.x - ball.size
                        ball.speed_x = -new_speed  # Move left
                    
                    # Add slight vertical component to prevent straight-line motion
                    ball.speed_y = new_speed * 0.2 * random.choice([-1, 1])
                    
                    # Clean up Redis keys
                    r.delete(f"{game_id}:ball_stuck_to_{stuck_side}")
                    r.delete(f"{game_id}:sticky_start_{stuck_side}")
                    r.delete(f"{game_id}:sticky_relative_pos_{stuck_side}")
                    r.delete(f"{game_id}:ball_original_speed_x")
                    r.delete(f"{game_id}:ball_original_speed_y")
                    
                    ball_moved = True
                else:
                    # Update ball position to follow paddle
                    paddle_y = float(r.get(f"{game_id}:paddle_{stuck_side}_y") or current_paddle.y)
                    if stuck_side == 'left':
                        ball.x = paddle_left.x + paddle_left.width + ball.size
                    else:
                        ball.x = paddle_right.x - ball.size
                    ball.y = paddle_y + relative_pos
                    ball_moved = True
            
            if not ball_moved:
                ball.move()
            
            await update_ball_redis(game_id, ball)

            # 3. Vérifier les collisions
            collision = await check_collisions(game_id, paddle_left, paddle_right, ball, bumpers, powerup_orbs)
            if collision in ['score_left', 'score_right']:
                await handle_score(game_id, collision)
                # print(f"[game_loop.py] game_id={game_id} - Handling score for {collision}")
                
                # Vérifier si quelqu'un a gagné
                score_left = int(r.get(f"{game_id}:score_left") or 0)
                score_right = int(r.get(f"{game_id}:score_right") or 0)
                if score_left >= WIN_SCORE or score_right >= WIN_SCORE:
                    # On arrête la boucle si la partie est terminée
                    break
                else:
                    # Personne n'a encore gagné,
                    # on réinitialise la balle pour continuer la partie
                    terrain_rect = await get_terrain_rect(game_id)
                    center_x = terrain_rect['left'] + terrain_rect['width'] // 2
                    center_y = terrain_rect['top'] + terrain_rect['height'] // 2
                    ball.reset(center_x, center_y, 4, 4)  # Vitesse X/Y à ajuster
                    await update_ball_redis(game_id, ball)
                    print(f"[game_loop.py] Ball reset to ({ball.x}, {ball.y}) with speed ({ball.speed_x}, {ball.speed_y})")

            # 4. Gérer les power-ups
            if parameters.bonus_malus_activation:
                if current_time - last_powerup_spawn_time >= powerup_spawn_interval:
                    # Tenter de spawn un power-up
                    active_powerups = await count_active_powerups(game_id, powerup_orbs)
                    # print(f"[game_loop.py] game_id={game_id} - Active power-ups: {active_powerups}")
                    if active_powerups < 2:  # MAX_ACTIVE_POWERUPS = 2
                        powerup_orb = random.choice(powerup_orbs)
                        if not powerup_orb.active:
                            spawned = await spawn_powerup(game_id, powerup_orb)
                            if spawned:
                                last_powerup_spawn_time = current_time
                                print(f"[game_loop.py] game_id={game_id} - PowerUp {powerup_orb.effect_type} spawned.")

            # 5. Gérer les bumpers
            if parameters.bumpers_activation:
                if current_time - last_bumper_spawn_time >= bumper_spawn_interval:
                    # Tenter de spawn un bumper
                    active_bumpers = await count_active_bumpers(game_id, bumpers)
                    # print(f"[game_loop.py] game_id={game_id} - Active bumpers: {active_bumpers}")
                    if active_bumpers < 2:  # MAX_BUMPERS = 2
                        bumper = random.choice(bumpers)
                        if not bumper.active:
                            spawned = await spawn_bumper(game_id, bumper)
                            if spawned:
                                last_bumper_spawn_time = current_time
                                print(f"[game_loop.py] game_id={game_id} - Bumper spawned at ({bumper.x}, {bumper.y}).")

            # 6. Gérer les power-ups expirés
            await handle_powerup_expiration(game_id, powerup_orbs)
            # print(f"[game_loop.py] game_id={game_id} - Handled power-up expiration.")

            # 7. Gérer les bumpers expirés
            await handle_bumper_expiration(game_id, bumpers)
            # print(f"[game_loop.py] game_id={game_id} - Handled bumper expiration.")

            # 8. Broadcast l'état actuel du jeu
            await broadcast_game_state(game_id, channel_layer, paddle_left, paddle_right, ball, powerup_orbs, bumpers)
            # print(f"[game_loop.py] game_id={game_id} - Broadcasted game state.")

            # Attendre le prochain cycle
            await asyncio.sleep(dt)
    
    except Exception as e:
        print(f"[game_loop.py] game_id={game_id} encountered an exception: {e}")
    
    finally:
        print(f"[game_loop.py] game_id={game_id} loop ended.")

async def update_paddles_from_redis(game_id, paddle_left, paddle_right):
    """Updates paddle positions considering active effects."""
    left_vel = float(r.get(f"{game_id}:paddle_left_velocity") or 0)
    right_vel = float(r.get(f"{game_id}:paddle_right_velocity") or 0)

    # Apply speed boost if active
    if r.get(f"{game_id}:paddle_left_speed_boost"):
        left_vel *= 1.5  # 50% speed increase
    if r.get(f"{game_id}:paddle_right_speed_boost"):
        right_vel *= 1.5  # 50% speed increase

    # Convert velocity to direction
    left_direction = 0 if left_vel == 0 else (1 if left_vel > 0 else -1)
    right_direction = 0 if right_vel == 0 else (1 if right_vel > 0 else -1)

    # Apply inverted controls first
    if r.get(f"{game_id}:paddle_left_inverted"):
        left_direction *= -1
        left_vel *= -1
    if r.get(f"{game_id}:paddle_right_inverted"):
        right_direction *= -1
        right_vel *= -1

    # Check ice effects
    left_on_ice = bool(r.get(f"{game_id}:paddle_left_ice_effect"))
    right_on_ice = bool(r.get(f"{game_id}:paddle_right_ice_effect"))

    # Get current paddle heights from Redis
    left_height = float(r.get(f"{game_id}:paddle_left_height") or paddle_left.height)
    right_height = float(r.get(f"{game_id}:paddle_right_height") or paddle_right.height)

    # Define boundaries
    TOP_BOUNDARY = 50
    BOTTOM_BOUNDARY = 350  # This is the bottom border of the play area

    # Move paddles with ice physics if active, otherwise normal movement
    if left_on_ice:
        paddle_left.move(left_direction, left_on_ice, TOP_BOUNDARY, BOTTOM_BOUNDARY)
    else:
        # Update position
        paddle_left.y += left_vel
        # Constrain movement using current height
        # Bottom boundary is the maximum y position where the paddle can be placed
        paddle_left.y = max(TOP_BOUNDARY, min(BOTTOM_BOUNDARY - left_height, paddle_left.y))

    if right_on_ice:
        paddle_right.move(right_direction, right_on_ice, TOP_BOUNDARY, BOTTOM_BOUNDARY)
    else:
        # Update position
        paddle_right.y += right_vel
        # Constrain movement using current height
        paddle_right.y = max(TOP_BOUNDARY, min(BOTTOM_BOUNDARY - right_height, paddle_right.y))

    # Store updated positions
    r.set(f"{game_id}:paddle_left_y", paddle_left.y)
    r.set(f"{game_id}:paddle_right_y", paddle_right.y)


async def get_game_status(game_id):
    """
    Récupère le statut de la partie depuis la base de données.
    """
    try:
        session = await sync_to_async(GameSession.objects.get)(pk=game_id)
        return session.status
    except GameSession.DoesNotExist:
        return 'finished'

async def get_game_parameters(game_id):
    """
    Récupère les paramètres (GameParameters) de la partie depuis la base de données.
    """
    try:
        session = await sync_to_async(GameSession.objects.get)(pk=game_id)
        parameters = await sync_to_async(getattr)(session, 'parameters', None)
        return parameters
    except GameSession.DoesNotExist:
        return None

async def initialize_redis(game_id, paddle_left, paddle_right, ball, powerup_orbs, bumpers):
    """
    Initialise les positions et vitesses dans Redis pour chaque objet.
    """
    # Positions initiales des paddles
    r.set(f"{game_id}:paddle_left_y", paddle_left.y)
    r.set(f"{game_id}:paddle_right_y", paddle_right.y)

    # Vélocités initiales des paddles (0 => immobiles)
    r.set(f"{game_id}:paddle_left_velocity", 0)
    r.set(f"{game_id}:paddle_right_velocity", 0)

    # Balle
    r.set(f"{game_id}:ball_x", ball.x)
    r.set(f"{game_id}:ball_y", ball.y)
    r.set(f"{game_id}:ball_vx", ball.speed_x)
    r.set(f"{game_id}:ball_vy", ball.speed_y)

    # Power-ups
    for powerup_orb in powerup_orbs:
        r.delete(f"{game_id}:powerup_{powerup_orb.effect_type}_active")
        r.delete(f"{game_id}:powerup_{powerup_orb.effect_type}_x")
        r.delete(f"{game_id}:powerup_{powerup_orb.effect_type}_y")

    # Bumpers
    for bumper in bumpers:
        r.delete(f"{game_id}:bumper_{bumper.x}_{bumper.y}_active")
        r.delete(f"{game_id}:bumper_{bumper.x}_{bumper.y}_x")
        r.delete(f"{game_id}:bumper_{bumper.x}_{bumper.y}_y")

async def update_ball_redis(game_id, ball):
    """
    Met à jour la position de la balle dans Redis.
    """
    r.set(f"{game_id}:ball_x", ball.x)
    r.set(f"{game_id}:ball_y", ball.y)
    r.set(f"{game_id}:ball_vx", ball.speed_x)
    r.set(f"{game_id}:ball_vy", ball.speed_y)

async def check_collisions(game_id, paddle_left, paddle_right, ball, bumpers, powerup_orbs):
    """
    Vérifie collisions ball/paddles/bumpers/bords, retourne 'score_left', 'score_right' ou None.
    """
    result = await handle_paddle_collisions(game_id, paddle_left, paddle_right, ball)
    if result:
        return result

    handle_border_collisions(ball)

    await handle_bumper_collision(game_id, ball, bumpers)

    await handle_powerup_collision(game_id, ball, powerup_orbs)

    return None


async def handle_paddle_collisions(game_id, paddle_left, paddle_right, ball): #added
    """
    Gère les collisions avec les paddles gauche et droite.
    """

    # Check if ball is stuck to any paddle
    left_stuck = bool(r.get(f"{game_id}:ball_stuck_to_left"))
    right_stuck = bool(r.get(f"{game_id}:ball_stuck_to_right"))

    # If ball is stuck, no need to check for collisions/scoring
    if left_stuck or right_stuck:
        return None

    # Left paddle
    if ball.x - ball.size <= paddle_left.x + paddle_left.width:
        if paddle_left.y <= ball.y <= paddle_left.y + paddle_left.height:
            ball.last_player = 'left'  # Mettre à jour le dernier joueur
            await handle_paddle_collision(game_id, 'left', paddle_left, ball)
            return None
        else:
            return 'score_right'

    # Right paddle
    if ball.x + ball.size >= paddle_right.x:
        if paddle_right.y <= ball.y <= paddle_right.y + paddle_right.height:
            ball.last_player = 'right'  # Mettre à jour le dernier joueur
            await handle_paddle_collision(game_id, 'right', paddle_right, ball)
            return None
        else:
            return 'score_left'

    return None


def handle_border_collisions(ball):
    """
    Gère les collisions avec les bords supérieur et inférieur.
    """
    if ball.y - ball.size <= 50:
        ball.speed_y = abs(ball.speed_y)  # Rebond vers le bas
    elif ball.y + ball.size >= 350:
        ball.speed_y = -abs(ball.speed_y)  # Rebond vers le haut



async def handle_bumper_collision(game_id, ball, bumpers):
    # Bumpers
    current_time = time.time()
    for bumper in bumpers:
        if bumper.active:
            dist = math.hypot(ball.x - bumper.x, ball.y - bumper.y)
            if dist <= ball.size + bumper.size:
                if current_time - bumper.last_collision_time >= COOLDOWN_TIME:
                    angle = math.atan2(ball.y - bumper.y, ball.x - bumper.x)
                    speed = math.hypot(ball.speed_x, ball.speed_y) * 1.05
                    ball.speed_x = speed * math.cos(angle)
                    ball.speed_y = speed * math.sin(angle)

                    # Mettre à jour la balle dans Redis
                    await update_ball_redis(game_id, ball)

                    # Mettre à jour le temps de la dernière collision
                    bumper.last_collision_time = current_time

                    print(f"[game_loop.py] Ball collided with bumper at ({bumper.x}, {bumper.y}). New speed: ({ball.speed_x}, {ball.speed_y})")


async def handle_paddle_collision(game_id, paddle_side, paddle, ball):
    """Handles paddle collision with improved sticky effect."""
    
    # Check if sticky power-up is active for this paddle
    is_sticky = bool(r.get(f"{game_id}:paddle_{paddle_side}_sticky"))
    
    if is_sticky:
        # Calculate relative position where ball hit the paddle
        relative_pos = ball.y - paddle.y
        
        if 0 <= relative_pos <= paddle.height:  # Only stick if within paddle bounds
            # Store the original ball speed for later use
            r.set(f"{game_id}:ball_original_speed_x", ball.speed_x)
            r.set(f"{game_id}:ball_original_speed_y", ball.speed_y)
            
            # Set sticky state in Redis
            r.set(f"{game_id}:ball_stuck_to_{paddle_side}", 1)
            r.set(f"{game_id}:sticky_start_{paddle_side}", time.time())
            r.set(f"{game_id}:sticky_relative_pos_{paddle_side}", relative_pos)
            
            # Stop the ball
            ball.speed_x = 0
            ball.speed_y = 0
            
            # Position the ball exactly at the paddle
            if paddle_side == 'left':
                ball.x = paddle.x + paddle.width + ball.size
            else:
                ball.x = paddle.x - ball.size
            ball.y = paddle.y + relative_pos
    else:
        # Normal paddle collision mechanics
        relative_y = (ball.y - (paddle.y + paddle.height / 2)) / (paddle.height / 2)
        relative_y = max(-1, min(1, relative_y))
        angle = relative_y * (math.pi / 4)
        speed = math.hypot(ball.speed_x, ball.speed_y) * 1.03

        if paddle_side == 'left':
            ball.speed_x = speed * math.cos(angle)
        else:
            ball.speed_x = -speed * math.cos(angle)

        ball.speed_y = speed * math.sin(angle)
    
    await update_ball_redis(game_id, ball)

async def handle_powerup_collision(game_id, ball, powerup_orbs):
    """
    Vérifie si la balle a ramassé un power-up en dehors des collisions avec les paddles.
    """
    for powerup_orb in powerup_orbs:
        if powerup_orb.active:
            dist = math.hypot(ball.x - powerup_orb.x, ball.y - powerup_orb.y)
            if dist <= ball.size + powerup_orb.size:
                # Associer le power-up au dernier joueur qui a touché la balle
                last_player = ball.last_player
                if last_player:
                    await apply_powerup(game_id, last_player, powerup_orb)
                    powerup_orb.deactivate()
                    r.set(f"{game_id}:powerup_{powerup_orb.effect_type}_active", 0)
                    print(f"[game_loop.py] Player {last_player} collected power-up {powerup_orb.effect_type} at ({powerup_orb.x}, {powerup_orb.y})")
                else:
                    # Si aucun joueur n'a touché la balle récemment, attribuer au joueur gauche par défaut
                    await apply_powerup(game_id, 'left', powerup_orb)
                    powerup_orb.deactivate()
                    r.set(f"{game_id}:powerup_{powerup_orb.effect_type}_active", 0)
                    print(f"[game_loop.py] Player left collected power-up {powerup_orb.effect_type} at ({powerup_orb.x}, {powerup_orb.y}) by default")

async def apply_powerup(game_id, player, powerup_orb): #{added}
    """Applies the effect of the power-up."""
    print(f"[game_loop.py] Applying power-up {powerup_orb.effect_type} to {player}")

    # Create task for handling effect duration
    effect_duration = 5
    asyncio.create_task(handle_powerup_duration(game_id, player, powerup_orb))
    print(f"[game_loop.py] Creating duration task for {powerup_orb.effect_type}")

    # Deactivate the powerup immediately
    powerup_orb.deactivate()
    r.delete(f"{game_id}:powerup_{powerup_orb.effect_type}_active")
    r.delete(f"{game_id}:powerup_{powerup_orb.effect_type}_x")
    r.delete(f"{game_id}:powerup_{powerup_orb.effect_type}_y")

    # Notify clients immediately
    channel_layer = get_channel_layer()
    await channel_layer.group_send(
        f"pong_{game_id}",
        {
            'type': 'powerup_applied',
            'player': player,
            'effect': powerup_orb.effect_type,
            'duration': effect_duration  # 5 seconds duration
        }
    )

async def handle_powerup_duration(game_id, player, powerup_orb): #added
    """Handles the duration of a power-up effect asynchronously."""
    effect_type = powerup_orb.effect_type
    effect_duration = 5  # 5 seconds for all effects

    print(f"[game_loop.py] Starting effect {effect_type} for {player}")

    # Apply effect
    if effect_type == 'flash':
        r.set(f"{game_id}:flash_effect", 1)
        await asyncio.sleep(0.3) # Flash lasts 300ms
        r.delete(f"{game_id}:flash_effect")

    elif effect_type == 'shrink':
        opponent = 'left' if player == 'right' else 'right'
        print(f"[game_loop.py] Applying shrink to {opponent}")  # Debug log
        
        # Get current height and store it as original
        current_height = float(r.get(f"{game_id}:paddle_{opponent}_height") or 60)
        print(f"[game_loop.py] Original height: {current_height}")  # Debug log
        
        # Store original height for restoration
        r.set(f"{game_id}:paddle_{opponent}_original_height", current_height)
        
        # Calculate and set new height
        new_height = current_height * 0.5
        r.set(f"{game_id}:paddle_{opponent}_height", new_height)
        print(f"[game_loop.py] New height set to: {new_height}")  # Debug log
        
        # Wait for duration
        await asyncio.sleep(effect_duration)
    
        # Restore original height
        original_height = float(r.get(f"{game_id}:paddle_{opponent}_original_height") or 60)
        r.set(f"{game_id}:paddle_{opponent}_height", original_height)
        r.delete(f"{game_id}:paddle_{opponent}_original_height")
        print(f"[game_loop.py] Height restored to: {original_height}")  # Debug log

    elif effect_type == 'speed':
        # Set paddle speed multiplier
        r.set(f"{game_id}:paddle_{player}_speed_boost", 1)  # Flag for speed boost
        print(f"[game_loop.py] Speed boost applied to {player} paddle")
        
        await asyncio.sleep(effect_duration)
        
        # Remove speed boost
        r.delete(f"{game_id}:paddle_{player}_speed_boost")
        print(f"[game_loop.py] Speed boost removed from {player} paddle")

    elif effect_type == 'ice':
        opponent = 'left' if player == 'right' else 'right'
        r.set(f"{game_id}:paddle_{opponent}_ice_effect", 1)
        await asyncio.sleep(effect_duration)
        r.delete(f"{game_id}:paddle_{opponent}_ice_effect")

    elif effect_type == 'sticky':
        r.set(f"{game_id}:paddle_{player}_sticky", 1)
        await asyncio.sleep(effect_duration)
        r.delete(f"{game_id}:paddle_{player}_sticky")

    elif effect_type == 'invert':
        opponent = 'left' if player == 'right' else 'right'
        r.set(f"{game_id}:paddle_{opponent}_inverted", 1)
        await asyncio.sleep(effect_duration)
        r.delete(f"{game_id}:paddle_{opponent}_inverted")


async def handle_score(game_id, scorer):
    """
    Gère l'incrément du score, vérifie si la partie est terminée.
    """
    if scorer == 'score_left':
        score_left = int(r.get(f"{game_id}:score_left") or 0) + 1
        r.set(f"{game_id}:score_left", score_left)
        print(f"[game_loop.py] Player Left scored. Score: {score_left} - {r.get(f'{game_id}:score_right')}")
        if score_left >= WIN_SCORE:
            await finish_game(game_id, 'left')
    elif scorer == 'score_right':
        score_right = int(r.get(f"{game_id}:score_right") or 0) + 1
        r.set(f"{game_id}:score_right", score_right)
        print(f"[game_loop.py] Player Right scored. Score: {r.get(f'{game_id}:score_left')} - {score_right}")
        if score_right >= WIN_SCORE:
            await finish_game(game_id, 'right')

async def finish_game(game_id, winner):
    """
    Termine la partie, notifie, supprime les clés Redis, enregistre GameResult.
    """
    print(f"[game_loop.py] Game {game_id} finished, winner={winner}")
    channel_layer = get_channel_layer()
    try:
        session = await sync_to_async(GameSession.objects.get)(pk=game_id)
        session.status = 'finished'
        await sync_to_async(session.save)()

        score_left = int(r.get(f"{game_id}:score_left") or 0)
        score_right = int(r.get(f"{game_id}:score_right") or 0)
        await sync_to_async(GameResult.objects.create)(
            game=session,
            winner=winner,
            score_left=score_left,
            score_right=score_right
        )
        print(f"[game_loop.py] GameResult created for game_id={game_id}, winner={winner}")
    except GameSession.DoesNotExist:
        print(f"[game_loop.py] GameSession {game_id} does not exist.")
        pass

    # Notifier
    await channel_layer.group_send(
        f"pong_{game_id}",
        {
            'type': 'game_over',
            'winner': winner
        }
    )
    # print(f"[game_loop.py] Broadcast game_over for game_id={game_id}, winner={winner}")

    # Nettoyer les clés Redis
    keys = list(r.scan_iter(f"{game_id}:*"))
    for key in keys:
        r.delete(key)
    print(f"[game_loop.py] Redis keys deleted for game_id={game_id}")

async def spawn_powerup(game_id, powerup_orb):
    if powerup_orb.active:
        print(f"[game_loop.py] PowerUp {powerup_orb.effect_type} is already active, skipping spawn.")
        return False

    terrain_rect = await get_terrain_rect(game_id)
    if await sync_to_async(powerup_orb.spawn)(terrain_rect):
        r.set(f"{game_id}:powerup_{powerup_orb.effect_type}_active", 1)
        r.set(f"{game_id}:powerup_{powerup_orb.effect_type}_x", powerup_orb.x)
        r.set(f"{game_id}:powerup_{powerup_orb.effect_type}_y", powerup_orb.y)
        print(f"[game_loop.py] PowerUp {powerup_orb.effect_type} spawned at ({powerup_orb.x}, {powerup_orb.y})")
        return True
    return False

async def spawn_bumper(game_id, bumper):
    terrain_rect = await get_terrain_rect(game_id)
    if await sync_to_async(bumper.spawn)(terrain_rect):
        key = f"{game_id}:bumper_{bumper.x}_{bumper.y}_active"
        r.set(key, 1)
        r.set(f"{game_id}:bumper_{bumper.x}_{bumper.y}_x", bumper.x)
        r.set(f"{game_id}:bumper_{bumper.x}_{bumper.y}_y", bumper.y)
        print(f"[game_loop.py] Bumper spawned at ({bumper.x}, {bumper.y})")
        return True
    return False

async def count_active_powerups(game_id, powerup_orbs):
    """
    Compte le nombre de power-ups actifs.
    """
    count = 0
    for powerup_orb in powerup_orbs:
        active = r.get(f"{game_id}:powerup_{powerup_orb.effect_type}_active")
        if active and active.decode('utf-8') == '1':
            count += 1
    print(f"[game_loop.py] count_active_powerups ({count})")
    return count


async def count_active_bumpers(game_id, bumpers):
    """
    Compte le nombre de bumpers actifs.
    """
    count = 0
    for bumper in bumpers:
        active = r.get(f"{game_id}:bumper_{bumper.x}_{bumper.y}_active")
        if active and active.decode('utf-8') == '1':
            count += 1
    print(f"[game_loop.py] count_active_bumpers ({count})")
    return count


async def handle_powerup_expiration(game_id, powerup_orbs):
    current_time = time.time()
    for powerup_orb in powerup_orbs:
        if powerup_orb.active and current_time - powerup_orb.spawn_time >= powerup_orb.duration:
            powerup_orb.deactivate()
            r.delete(f"{game_id}:powerup_{powerup_orb.effect_type}_active")
            r.delete(f"{game_id}:powerup_{powerup_orb.effect_type}_x")
            r.delete(f"{game_id}:powerup_{powerup_orb.effect_type}_y")
            print(f"[game_loop.py] PowerUp {powerup_orb.effect_type} expired at ({powerup_orb.x}, {powerup_orb.y})")

async def handle_bumper_expiration(game_id, bumpers):
    """
    Gère l'expiration des bumpers.
    """
    current_time = time.time()
    for bumper in bumpers:
        if bumper.active and current_time - bumper.spawn_time >= bumper.duration:
            bumper.deactivate()
            key = f"{game_id}:bumper_{bumper.x}_{bumper.y}_active"
            r.set(key, 0)
            print(f"[game_loop.py] Bumper at ({bumper.x}, {bumper.y}) expired")


async def broadcast_game_state(game_id, channel_layer, paddle_left, paddle_right, ball, powerup_orbs, bumpers): #added
    """
    Envoie l'état actuel du jeu aux clients via WebSocket.
    """
    # Récupérer les états des power-ups
    powerups = []
    for powerup_orb in powerup_orbs:
        active = r.get(f"{game_id}:powerup_{powerup_orb.effect_type}_active")
        if active and active.decode('utf-8') == '1':
            x = float(r.get(f"{game_id}:powerup_{powerup_orb.effect_type}_x"))
            y = float(r.get(f"{game_id}:powerup_{powerup_orb.effect_type}_y"))
            powerups.append({
                'type': powerup_orb.effect_type,
                'x': x,
                'y': y,
                'color': list(powerup_orb.color)  # Convertir en liste pour JSON
            })

    # Récupérer les états des bumpers
    active_bumpers = []
    for bumper in bumpers:
        key = f"{game_id}:bumper_{bumper.x}_{bumper.y}_active"
        active = r.get(key)
        if active and active.decode('utf-8') == '1':
            active_bumpers.append({
                'x': bumper.x,
                'y': bumper.y,
                'size': bumper.size,
                'color': list(bumper.color)  # Convertir en liste pour JSON
            })

    data = {
        'type': 'game_state',
        'ball_x': ball.x,
        'ball_y': ball.y,
        'ball_size': ball.size,
        'ball_speed_x': ball.speed_x,
        'ball_speed_y': ball.speed_y,
        'paddle_left_y': paddle_left.y,
        'paddle_right_y': paddle_right.y,
        'paddle_width': paddle_left.width,
        'paddle_left_height': float(r.get(f"{game_id}:paddle_left_height") or paddle_left.height),
        'paddle_right_height': float(r.get(f"{game_id}:paddle_right_height") or paddle_right.height),
        'score_left': int(r.get(f"{game_id}:score_left") or 0),
        'score_right': int(r.get(f"{game_id}:score_right") or 0),
        'powerups': powerups,
        'bumpers': active_bumpers,
        'flash_effect': bool(r.get(f"{game_id}:flash_effect"))
    }

    await channel_layer.group_send(f"pong_{game_id}", {
        'type': 'broadcast_game_state',
        'data': data
    })
    # print(f"[game_loop.py] Broadcast game_state for game_id={game_id}")

