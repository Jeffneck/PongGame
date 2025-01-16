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
WIN_SCORE = 10

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
    power_up_orbs = [
        PowerUpOrb(game_id, 'invert', terrain_rect),
        PowerUpOrb(game_id, 'shrink', terrain_rect),
        PowerUpOrb(game_id, 'ice', terrain_rect),
        PowerUpOrb(game_id, 'speed', terrain_rect),
        PowerUpOrb(game_id, 'flash', terrain_rect),
        PowerUpOrb(game_id, 'sticky', terrain_rect)
    ]

    bumpers = []
    if parameters.bumpers_activation:
        bumpers = [Bumper(game_id, terrain_rect) for _ in range(3)]  # Adjust number as needed

    return paddle_left, paddle_right, ball, power_up_orbs, bumpers

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
        paddle_left, paddle_right, ball, power_up_orbs, bumpers = await initialize_game_objects(game_id, parameters)
        print(f"[game_loop.py] Game objects initialized for game_id={game_id}.")
        
        # Initialiser les positions et vélocités dans Redis
        await initialize_redis(game_id, paddle_left, paddle_right, ball, power_up_orbs, bumpers)
        print(f"[game_loop.py] Game objects positions initialized in Redis for game_id={game_id}.")
        
        last_powerup_spawn_time = time.time()
        powerup_spawn_interval = 10  # Adjust as needed

        last_bumper_spawn_time = time.time()
        bumper_spawn_interval = 15  # Adjust as needed

        while True:
            current_time = time.time()
            print(f"[game_loop.py] game_id={game_id} - Loop iteration at {current_time}")

            # Vérifier si la partie est encore "running"
            session_status = await get_game_status(game_id)
            print(f"[game_loop.py] game_id={game_id} - Session status: {session_status}")
            if session_status != 'running':
                print(f"[game_loop.py] game_id={game_id} is not running (status={session_status}), breaking loop.")
                break

            # 1. Mettre à jour les positions des raquettes depuis Redis en fonction de la vélocité
            await update_paddles_from_redis(game_id, paddle_left, paddle_right)
            print(f"[game_loop.py] game_id={game_id} - Paddles positions updated from Redis.")

            # 2. Mettre à jour la position de la balle
            ball.move()
            await update_ball_redis(game_id, ball)
            print(f"[game_loop.py] game_id={game_id} - Ball position updated to ({ball.x}, {ball.y})")

            # 3. Vérifier les collisions
            collision = await check_collisions(game_id, paddle_left, paddle_right, ball, bumpers, power_up_orbs)
            if collision in ['score_left', 'score_right']:
                await handle_score(game_id, collision)
                print(f"[game_loop.py] game_id={game_id} - Handling score for {collision}")
                
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
                    active_powerups = await count_active_powerups(game_id, power_up_orbs)
                    print(f"[game_loop.py] game_id={game_id} - Active power-ups: {active_powerups}")
                    if active_powerups < 2:  # MAX_ACTIVE_POWERUPS = 2
                        orb = random.choice(power_up_orbs)
                        if not orb.active:
                            spawned = await spawn_powerup(game_id, orb)
                            if spawned:
                                last_powerup_spawn_time = current_time
                                print(f"[game_loop.py] game_id={game_id} - PowerUp {orb.effect_type} spawned.")

            # 5. Gérer les bumpers
            if parameters.bumpers_activation:
                if current_time - last_bumper_spawn_time >= bumper_spawn_interval:
                    # Tenter de spawn un bumper
                    active_bumpers = await count_active_bumpers(game_id, bumpers)
                    print(f"[game_loop.py] game_id={game_id} - Active bumpers: {active_bumpers}")
                    if active_bumpers < 2:  # MAX_BUMPERS = 2
                        bumper = random.choice(bumpers)
                        if not bumper.active:
                            spawned = await spawn_bumper(game_id, bumper)
                            if spawned:
                                last_bumper_spawn_time = current_time
                                print(f"[game_loop.py] game_id={game_id} - Bumper spawned at ({bumper.x}, {bumper.y}).")

            # 6. Gérer les power-ups expirés
            await handle_powerup_expiration(game_id, power_up_orbs)
            print(f"[game_loop.py] game_id={game_id} - Handled power-up expiration.")

            # 7. Gérer les bumpers expirés
            await handle_bumper_expiration(game_id, bumpers)
            print(f"[game_loop.py] game_id={game_id} - Handled bumper expiration.")

            # 8. Broadcast l'état actuel du jeu
            await broadcast_game_state(game_id, channel_layer, paddle_left, paddle_right, ball, power_up_orbs, bumpers)
            print(f"[game_loop.py] game_id={game_id} - Broadcasted game state.")

            # Attendre le prochain cycle
            await asyncio.sleep(dt)
    
    except Exception as e:
        print(f"[game_loop.py] game_id={game_id} encountered an exception: {e}")
    
    finally:
        print(f"[game_loop.py] game_id={game_id} loop ended.")

async def update_paddles_from_redis(game_id, paddle_left, paddle_right):
    """
    Lit la vélocité dans Redis et met à jour la position (y) des paddles.
    """
    left_vel = float(r.get(f"{game_id}:paddle_left_velocity") or 0)
    right_vel = float(r.get(f"{game_id}:paddle_right_velocity") or 0)

    # Appliquer la vélocité
    paddle_left.y += left_vel
    paddle_right.y += right_vel

    # Contraindre le mouvement dans [50, 350 - paddle.height]
    paddle_left.y = max(50, min(350 - paddle_left.height, paddle_left.y))
    paddle_right.y = max(50, min(350 - paddle_right.height, paddle_right.y))

    # Stocker la position mise à jour
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

async def initialize_redis(game_id, paddle_left, paddle_right, ball, power_up_orbs, bumpers):
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
    for orb in power_up_orbs:
        r.delete(f"{game_id}:powerup_{orb.effect_type}_active")
        r.delete(f"{game_id}:powerup_{orb.effect_type}_x")
        r.delete(f"{game_id}:powerup_{orb.effect_type}_y")

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

async def check_collisions(game_id, paddle_left, paddle_right, ball, bumpers, power_up_orbs):
    """
    Vérifie collisions ball/paddles/bumpers/bords, retourne 'score_left', 'score_right' ou None.
    """
    # Left paddle
    if ball.x - ball.size <= paddle_left.x + paddle_left.width:
        if paddle_left.y <= ball.y <= paddle_left.y + paddle_left.height:
            await handle_paddle_collision(game_id, 'left', paddle_left, ball)
            await check_powerup_collection(game_id, 'left', ball, power_up_orbs)
            return None
        else:
            return 'score_right'

    # Right paddle
    if ball.x + ball.size >= paddle_right.x:
        if paddle_right.y <= ball.y <= paddle_right.y + paddle_right.height:
            await handle_paddle_collision(game_id, 'right', paddle_right, ball)
            await check_powerup_collection(game_id, 'right', ball, power_up_orbs)
            return None
        else:
            return 'score_left'

    # Bords haut/bas
    if ball.y - ball.size <= 50:
        ball.speed_y = abs(ball.speed_y)  # Rebond vers le bas
    elif ball.y + ball.size >= 350:
        ball.speed_y = -abs(ball.speed_y)  # Rebond vers le haut

    # Bumpers
    for bumper in bumpers:
        if bumper.active:
            dist = math.hypot(ball.x - bumper.x, ball.y - bumper.y)
            if dist <= ball.size + bumper.size:
                angle = math.atan2(ball.y - bumper.y, ball.x - bumper.x)
                speed = math.hypot(ball.speed_x, ball.speed_y) * 1.05
                ball.speed_x = speed * math.cos(angle)
                ball.speed_y = speed * math.sin(angle)
                print(f"[game_loop.py] Ball collided with bumper at ({bumper.x}, {bumper.y}). New speed: ({ball.speed_x}, {ball.speed_y})")

    return None

async def handle_paddle_collision(game_id, paddle_side, paddle, ball):
    """
    Gère la logique de collision entre la balle et une raquette.
    """
    relative_y = (ball.y - (paddle.y + paddle.height / 2)) / (paddle.height / 2)
    relative_y = max(-1, min(1, relative_y))  # Limiter à l'intervalle [-1, 1]

    angle = relative_y * (math.pi / 4)  # Max 45 degrés
    speed = math.hypot(ball.speed_x, ball.speed_y) * 1.03  # Augmenter la vitesse

    if paddle_side == 'left':
        ball.speed_x = speed * math.cos(angle)
    else:
        ball.speed_x = -speed * math.cos(angle)

    ball.speed_y = speed * math.sin(angle)

    # Mettre à jour la balle dans Redis
    await update_ball_redis(game_id, ball)

    print(f"[game_loop.py] Ball collided with {paddle_side} paddle. New speed: ({ball.speed_x}, {ball.speed_y})")

async def check_powerup_collection(game_id, player, ball, power_up_orbs):
    """
    Vérifie si la balle a ramassé un power-up.
    """
    for orb in power_up_orbs:
        if orb.active:
            dist = math.hypot(ball.x - orb.x, ball.y - orb.y)
            if dist <= ball.size + orb.size:
                await apply_powerup(game_id, player, orb)
                orb.deactivate()
                r.set(f"{game_id}:powerup_{orb.effect_type}_active", 0)
                print(f"[game_loop.py] Player {player} collected power-up {orb.effect_type} at ({orb.x}, {orb.y})")

async def apply_powerup(game_id, player, orb):
    """
    Applique l'effet du power-up au joueur.
    """
    # Implémenter la logique d'application des effets
    print(f"[game_loop.py] Applying power-up {orb.effect_type} to {player}")

    # Exemple de notification
    channel_layer = get_channel_layer()
    effect = orb.effect_type
    await channel_layer.group_send(
        f"pong_{game_id}",
        {
            'type': 'powerup_applied',
            'player': player,
            'effect': effect
        }
    )

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
    print(f"[game_loop.py] Broadcast game_over for game_id={game_id}, winner={winner}")

    # Nettoyer les clés Redis
    keys = list(r.scan_iter(f"{game_id}:*"))
    for key in keys:
        r.delete(key)
    print(f"[game_loop.py] Redis keys deleted for game_id={game_id}")

async def spawn_powerup(game_id, orb):
    terrain_rect = await get_terrain_rect(game_id)
    if await sync_to_async(orb.spawn)(terrain_rect):
        r.set(f"{game_id}:powerup_{orb.effect_type}_active", 1)
        r.set(f"{game_id}:powerup_{orb.effect_type}_x", orb.x)
        r.set(f"{game_id}:powerup_{orb.effect_type}_y", orb.y)
        print(f"[game_loop.py] PowerUp {orb.effect_type} spawned at ({orb.x}, {orb.y})")
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

async def count_active_powerups(game_id, power_up_orbs):
    """
    Compte le nombre de power-ups actifs.
    """
    count = 0
    for orb in power_up_orbs:
        if r.get(f"{game_id}:powerup_{orb.effect_type}_active"):
            count += 1
    return count

async def count_active_bumpers(game_id, bumpers):
    """
    Compte le nombre de bumpers actifs.
    """
    count = 0
    for bumper in bumpers:
        if r.get(f"{game_id}:bumper_{bumper.x}_{bumper.y}_active"):
            count += 1
    return count

async def handle_powerup_expiration(game_id, power_up_orbs):
    """
    Gère l'expiration des power-ups.
    """
    current_time = time.time()
    for orb in power_up_orbs:
        if orb.active and current_time - orb.spawn_time >= orb.duration:
            orb.deactivate()
            r.set(f"{game_id}:powerup_{orb.effect_type}_active", 0)
            print(f"[game_loop.py] PowerUp {orb.effect_type} expired at ({orb.x}, {orb.y})")

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

async def broadcast_game_state(game_id, channel_layer, paddle_left, paddle_right, ball, power_up_orbs, bumpers):
    """
    Envoie l'état actuel du jeu aux clients via WebSocket.
    """
    # Récupérer les états des power-ups
    powerups = []
    for orb in power_up_orbs:
        if r.get(f"{game_id}:powerup_{orb.effect_type}_active"):
            x = float(r.get(f"{game_id}:powerup_{orb.effect_type}_x"))
            y = float(r.get(f"{game_id}:powerup_{orb.effect_type}_y"))
            powerups.append({
                'type': orb.effect_type,
                'x': x,
                'y': y,
                'color': list(orb.color)  # Convertir en liste pour JSON
            })

    # Récupérer les états des bumpers
    active_bumpers = []
    for bumper in bumpers:
        key = f"{game_id}:bumper_{bumper.x}_{bumper.y}_active"
        if r.get(key):
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
        'paddle_left_height': paddle_left.height,
        'paddle_right_height': paddle_right.height,
        'score_left': int(r.get(f"{game_id}:score_left") or 0),
        'score_right': int(r.get(f"{game_id}:score_right") or 0),
        'powerups': powerups,
        'bumpers': active_bumpers,
    }

    await channel_layer.group_send(f"pong_{game_id}", {
        'type': 'broadcast_game_state',
        'data': data
    })
    print(f"[game_loop.py] Broadcast game_state for game_id={game_id}")
