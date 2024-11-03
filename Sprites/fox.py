# fox.py

import pygame
import os
import sys
import math
import random
from Sprites.powerup import Powerup  # Import Powerup for spawning powerups

class Fox(pygame.sprite.Sprite):
    def __init__(self, image_path, bush_level):
        super().__init__()
        try:
            self.image = pygame.image.load(image_path).convert_alpha()
        except pygame.error as e:
            print(f"Unable to load fox image at {image_path}: {e}")
            pygame.quit()
            sys.exit()
        self.image = pygame.transform.scale(self.image, (60, 60))
        self.x = 820  # Start off-screen on the right

        # Map bush levels to specific y-coordinates
        bush_y_coordinates = {
            'bottom': 543,
            'lower': 393,
            'middle': 256,
            'upper': 113
        }
        self.bush_level = bush_y_coordinates.get(bush_level, 543)
        self.y = self.bush_level

        # Set random speed and corresponding bounce height
        self.vx = random.choice([1, 2, 3, 4])  # Speed options for fox
        if self.vx == 1:
            self.bounce_height = 5  # Small hop for slow speed
        elif self.vx == 2:
            self.bounce_height = 8
        elif self.vx == 3:
            self.bounce_height = 10
        else:
            self.bounce_height = 12  # Highest hop for fastest speed

        self.max_bounce_height = self.bush_level - self.bounce_height
        self.y = self.max_bounce_height

        self.rect = self.image.get_rect(topleft=(self.x, self.y))

        self.is_hit = False
        self.hit_timer = 0
        self.can_drop_powerup = True  # Track whether the fox can drop a power-up
        self.is_fed = False  # Attribute for fed status
        self.vibration_amplitude = 5
        self.vibration_speed = 20
        self.original_x = self.x

    def update(self, dt):
        if self.is_hit:
            self.hit_timer -= dt
            # Vibrate in place
            self.x = self.original_x + self.vibration_amplitude * math.sin(self.hit_timer * self.vibration_speed)
            if self.hit_timer <= 0:
                self.is_hit = False
                self.is_fed = True  # Ensure fox remains fed after vibration
                self.vx = random.choice([1, 2, 3, 4])
                self.x = self.original_x  # Reset position after vibration
        else:
            self.x -= self.vx
            self.bounce_logic(dt)
            self.rect.topleft = (self.x, self.y)
            self.original_x = self.x  # Update original_x when moving

        # Update the rectangle position
        self.rect.x = self.x
        self.rect.y = self.y

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
        if ammo_type == "berry" and not self.is_fed:
            self.is_hit = True
            self.hit_timer = 2  # Fox stops and vibrates for 2 seconds
            self.vx = 0
            # Play eat2.mp3 sound
            sound_path = os.path.join("D:/Projects/FoodThrowGame2/sound", "eat2.mp3")
            try:
                eat_sound = pygame.mixer.Sound(sound_path)
                eat_sound.play()
            except pygame.error as e:
                print(f"Unable to load sound at {sound_path}: {e}")
            if self.can_drop_powerup:
                self.can_drop_powerup = False
                return self.drop_powerup()
        return None

    def drop_powerup(self):
        powerup_images = {
            "apple": os.path.join("D:/Projects/FoodThrowGame2/art", "apple.png"),
            "pineapple": os.path.join("D:/Projects/FoodThrowGame2/art", "pineapple.png"),
            "banana": os.path.join("D:/Projects/FoodThrowGame2/art", "banana.png"),
            "honey": os.path.join("D:/Projects/FoodThrowGame2/art", "honey.png"),
        }

        # Use weighted power-up drop logic
        return Powerup.spawn_weighted_for_fox((self.rect.x, self.rect.x + self.rect.width),
                                              (self.rect.y, self.rect.y + self.rect.height),
                                              powerup_images)
