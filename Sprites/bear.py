# bear.py

import pygame
import os
import random
import math
import sys
from Sprites.powerup import Powerup

class Bear(pygame.sprite.Sprite):
    def __init__(self, image_path, bush_level):
        super().__init__()
        try:
            self.image = pygame.image.load(image_path).convert_alpha()
        except pygame.error as e:
            print(f"Unable to load bear image at {image_path}: {e}")
            pygame.quit()
            sys.exit()
        self.image = pygame.transform.scale(self.image, (60, 60))
        self.x = 820  # Start off-screen on the right

        bush_y_coordinates = {
            'bottom': 543,
            'lower': 393,
            'middle': 256,
            'upper': 113
        }
        self.bush_level = bush_y_coordinates.get(bush_level, 543)
        self.vx = 0.5
        self.bounce_height = 12
        self.max_bounce_height = self.bush_level - self.bounce_height
        self.y = self.max_bounce_height

        self.rect = self.image.get_rect(topleft=(self.x, self.y))
        self.is_fed = False
        self.can_drop_powerup = True
        self.health = 100

        # New attributes for teleportation
        self.hit_count = 0
        self.teleporting = False
        self.descending_for_teleport = False

    def update(self, dt):
        if self.descending_for_teleport:
            self.descend_for_teleport()
        else:
            # Bear always moves towards the player
            self.x -= self.vx
            self.bounce_logic(dt)
            self.rect.topleft = (self.x, self.y)

    def bounce_logic(self, dt):
        self.y = self.max_bounce_height + int(self.bounce_height * math.sin(self.x / 20))

    def draw(self, screen, bushes):
        bush_lines = {
            'upper': (113, 150),
            'middle': (256, 293),
            'lower': (393, 430),
            'bottom': (543, 580)
        }

        for level, (top, bottom) in bush_lines.items():
            if self.rect.bottom > top and self.rect.top < bottom:
                visible_height = top - self.rect.top
                visible_rect = pygame.Rect(0, 0, self.rect.width, max(0, visible_height))
                screen.blit(self.image, self.rect.topleft, visible_rect)
                return

        screen.blit(self.image, self.rect)

    def on_hit(self, ammo_type):
        if ammo_type == "berry":
            self.health = max(0, self.health - 1)
        elif ammo_type == "honey":
            self.health = max(0, self.health - 10)

        if self.health <= 0:
            self.is_fed = True
            self.vx = 0  # Bear stops moving when defeated
            if self.can_drop_powerup:
                self.can_drop_powerup = False
                return self.drop_powerup()

        # Increment hit counter and check for teleportation
        self.hit_count += 1
        if self.hit_count >= 3:
            self.hit_count = 0
            if random.random() < 0.5:  # 50% chance to teleport
                self.start_teleport()
        return None

    def start_teleport(self):
        # Play teleportation sound
        sound_path = os.path.join("D:/Projects/FoodThrowGame2/sound", "eat.mp3")
        try:
            teleport_sound = pygame.mixer.Sound(sound_path)
            teleport_sound.play()
        except pygame.error as e:
            print(f"Unable to load sound at {sound_path}: {e}")

        self.descending_for_teleport = True

    def descend_for_teleport(self):
        # Move the bear downward until it reaches the lowest bounce point
        self.y = min(self.y + 5, self.bush_level)  # Adjust speed as needed
        self.rect.y = self.y
        if self.y >= self.bush_level:
            # Immediately teleport after reaching the lowest point
            self.descending_for_teleport = False
            self.teleport()

    def teleport(self):
        # Randomly select a new bush level
        new_bush_level = random.choice(['upper', 'middle', 'lower', 'bottom'])
        bush_y_coordinates = {
            'upper': 113,
            'middle': 256,
            'lower': 393,
            'bottom': 543
        }
        self.bush_level = bush_y_coordinates[new_bush_level]
        self.max_bounce_height = self.bush_level - self.bounce_height
        self.y = self.max_bounce_height
        self.rect.y = self.y

    def drop_powerup(self):
        honey_image = os.path.join("D:/Projects/FoodThrowGame2/art", "honey.png")
        if random.random() < 0.05:
            return Powerup("honey", *self.rect.center, honey_image)
        return None
