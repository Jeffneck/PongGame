# game/game_objects.py

import random
import math
import time

class Paddle: 
    def __init__(self, position, size, speed):
        """
        position: 'left' ou 'right'
        size: taille initiale de la raquette
        speed: vitesse de déplacement
        """
        self.position = position
        self.width = 10
        self.height = size
        self.x = 50 if position == 'left' else 750
        self.y = 200 - self.height // 2
        self.speed = speed
        self.velocity = 0
        # self.shown_size = size  # Current displayed size

    def move(self, direction, is_on_ice, terrain_top, terrain_bottom, speed_boost=False):
        ice_acceleration = 0.5
        ice_friction = 0.02
        if is_on_ice:
            if direction != 0:
                self.velocity += direction * ice_acceleration
            self.velocity *= (1 - ice_friction)
        else:
            speed = self.speed * 1.5 if speed_boost else self.speed
            self.velocity = direction * speed

        # Apply movement with boundary checking
        new_y = self.y + self.velocity
        if new_y < terrain_top:
            new_y = terrain_top
            self.velocity = 0
        elif new_y + self.height > terrain_bottom:
            new_y = terrain_bottom - self.height
            self.velocity = 0

        self.y = new_y

    def resize(self, new_height):
        self.height = new_height

class Ball:
    def __init__(self, x, y, speed_x, speed_y, size=7):
        self.x = x
        self.y = y
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.size = size
        self.last_player = None  # Nouvel attribut pour suivre le dernier joueur

    # def move(self):
    #     self.x += self.speed_x
    #     self.y += self.speed_y

    def reset(self, x, y, speed_x, speed_y):
        self.x = x
        self.y = y
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.last_player = None  # Réinitialiser le dernier joueur

class PowerUpOrb:
    def __init__(self, game_id, effect_type, terrain_rect, color=None):
        self.game_id = game_id
        self.effect_type = effect_type  # 'invert', 'shrink', 'ice', 'speed', 'sticky', 'flash'
        self.size = 15
        self.color = color or self.get_default_color()
        self.active = False
        self.x = 0
        self.y = 0
        self.rect = None
        self.spawn_time = 0
        self.duration = 10
        self.effect_duration = 5
        self.in_cooldown = False
        self.cooldown_end_time = 0

        # Define spawn area boundaries (25% to 75% of field width) / added
        self.spawn_area = {
            'left': terrain_rect['left'] + (terrain_rect['width'] * 0.25),
            'right': terrain_rect['left'] + (terrain_rect['width'] * 0.75),
            'top': terrain_rect['top'] + (terrain_rect['height'] * 0.1),
            'bottom': terrain_rect['top'] + (terrain_rect['height'] * 0.9)
        }

    def get_default_color(self):
        colors = {
            'invert': (255, 105, 180),  # Pink
            'shrink': (255, 0, 0),      # Red
            'ice': (0, 255, 255),       # Cyan
            'speed': (255, 215, 0),     # Gold
            'flash': (255, 255, 0),     # Yellow
            # 'sticky': (50, 205, 50)     # Lime green
        }
        return colors.get(self.effect_type, (255, 255, 255))

    def start_cooldown(self): # / added
        """Start cooldown period that prevents this type of powerup from spawning"""
        self.in_cooldown = True
        self.cooldown_end_time = time.time() + self.duration + self.effect_duration
        print(f"[PowerUpOrb] {self.effect_type} cooldown started until: {self.cooldown_end_time}")

    def check_cooldown(self): # / added
        """Check if powerup is in cooldown period"""
        if self.in_cooldown:
            if time.time() >= self.cooldown_end_time:
                self.in_cooldown = False
                print(f"[PowerUpOrb] {self.effect_type} cooldown ended")
                return False
            return True
        return False

    def check_position_valid(self, x, y, powerup_orbs, bumpers):
        # Check distance from other powerups / added
        MIN_POWERUP_DISTANCE = 40
        MIN_BUMPER_DISTANCE = 40

        #Debug count
        active_powerups = 0
        active_bumpers = 0

        for orb in powerup_orbs:
            if orb.active and orb != self:
                active_powerups += 1
                distance = math.hypot(x - orb.x, y - orb.y)
                print(f"[DEBUG] PowerUp checking distance to other powerup: {distance}")
                if distance < MIN_POWERUP_DISTANCE:
                    print(f"[DEBUG] PowerUp spawn rejected: too close to other powerup ({distance} < {MIN_POWERUP_DISTANCE})")
                    return False

        # Check distance from bumpers
        MIN_BUMPER_DISTANCE = 40
        for bumper in bumpers:
            if bumper.active:
                active_bumpers += 1
                distance = math.hypot(x - bumper.x, y - bumper.y)
                print(f"[DEBUG] PowerUp checking distance to bumper: {distance}")
                if distance < MIN_BUMPER_DISTANCE:
                    print(f"[DEBUG] PowerUp spawn rejected: too close to bumper ({distance} < {MIN_BUMPER_DISTANCE})")
                    return False
        print(f"[DEBUG] PowerUp spawn position check complete. Checked against {active_powerups} active powerups and {active_bumpers} active bumpers")
        return True

    def spawn(self, terrain_rect, powerup_orbs=None, bumpers=None):
        if self.active or self.check_cooldown():
            return False
        if powerup_orbs is None:
            powerup_orbs = []
        if bumpers is None:
            bumpers = []

        max_attempts = 100

        for attempt in range(max_attempts):
            # Spawn within the defined middle area / modified
            new_x = random.uniform(self.spawn_area['left'], self.spawn_area['right'])
            new_y = random.uniform(self.spawn_area['top'], self.spawn_area['bottom'])

            # Additional check to ensure better distribution in the middle
            center_x = terrain_rect['left'] + (terrain_rect['width'] / 2)
            if abs(new_x - center_x) < 50:  # If too close to center, try again
                continue

            # Check if position is valid (not too close to other objects) / added
            if self.check_position_valid(new_x, new_y, powerup_orbs, bumpers):
                self.x = new_x
                self.y = new_y
                self.rect = (self.x, self.y, self.size, self.size)
                self.active = True
                self.spawn_time = time.time()
                print(f"[DEBUG] Successfully spawned powerup after {attempt + 1} attempts")
                return True
            else:
                print(f"[DEBUG] Attempt {attempt + 1} failed validation")
        return False

    def activate(self):
        self.active = True
        self.spawn_time = time.time()

    def deactivate(self):
        self.active = False
        self.x = None
        self.y = None
        self.spawn_time = None
        self.start_cooldown()

class Bumper:
    def __init__(self, game_id, terrain_rect):
        self.game_id = game_id
        self.size = 20
        self.color = (255, 255, 255)  # White
        self.active = False
        self.x = 0
        self.y = 0
        self.rect = None
        self.spawn_time = 0
        self.duration = 10
        self.last_collision_time = 0 

        # Define spawn area boundaries (40% to 60% of field width for more central placement) / added
        self.spawn_area = {
            'left': terrain_rect['left'] + (terrain_rect['width'] * 0.25),
            'right': terrain_rect['left'] + (terrain_rect['width'] * 0.75),
            'top': terrain_rect['top'] + (terrain_rect['height'] * 0.1),
            'bottom': terrain_rect['top'] + (terrain_rect['height'] * 0.9)
        }

    def check_position_valid(self, x, y, powerup_orbs, bumpers): # / added
        # Check distance from powerups
        MIN_POWERUP_DISTANCE = 40
        MIN_BUMPER_DISTANCE = 40

        # Debug counters
        active_powerups = 0
        active_bumpers = 0

        for orb in powerup_orbs:
            if orb.active:
                active_powerups += 1
                distance = math.hypot(x - orb.x, y - orb.y)
                print(f"[DEBUG] Bumper checking distance to powerup: {distance}")
                if distance < MIN_POWERUP_DISTANCE:
                    print(f"[DEBUG] Bumper spawn rejected: too close to powerup ({distance} < {MIN_POWERUP_DISTANCE})")
                    return False

        # Check distance from other bumpers
        MIN_BUMPER_DISTANCE = 40
        for bumper in bumpers:
            if bumper.active and bumper != self:
                active_bumpers += 1
                distance = math.hypot(x - bumper.x, y - bumper.y)
                print(f"[DEBUG] Bumper checking distance to other bumper: {distance}")
                if distance < MIN_BUMPER_DISTANCE:
                    print(f"[DEBUG] Bumper spawn rejected: too close to other bumper ({distance} < {MIN_BUMPER_DISTANCE})")
                    return False
        print(f"[DEBUG] Bumper spawn position check complete. Checked against {active_powerups} active powerups and {active_bumpers} active bumpers")
        return True

    def spawn(self, terrain_rect, powerup_orbs=None, bumpers=None):
        if self.active:
            return False

        if powerup_orbs is None:
            powerup_orbs = []
        if bumpers is None:
            bumpers = []

        max_attempts = 100

        # left = terrain_rect['left']
        # right = terrain_rect['left'] + terrain_rect['width']
        # top = terrain_rect['top']
        # bottom = terrain_rect['top'] + terrain_rect['height'] / removed

        for _ in range(max_attempts):
            # Spawn within the defined middle area / modified
            new_x = random.uniform(self.spawn_area['left'], self.spawn_area['right'])
            new_y = random.uniform(self.spawn_area['top'], self.spawn_area['bottom'])

            # Check distance from center to avoid too much clustering
            center_x = terrain_rect['left'] + (terrain_rect['width'] / 2)
            center_y = terrain_rect['top'] + (terrain_rect['height'] / 2)
            dist_to_center = math.hypot(new_x - center_x, new_y - center_y)
            
            if dist_to_center < 30:  # If too close to center, try again
                continue

            # Check if position is valid (not too close to other objects)
            if self.check_position_valid(new_x, new_y, powerup_orbs, bumpers):
                self.x = new_x
                self.y = new_y
                self.rect = (self.x, self.y, self.size, self.size)
                self.active = True
                self.spawn_time = time.time()
                return True

        return False
    
    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False
