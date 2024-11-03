# rabbit.py

import pygame
import os
import sys
import random
from Sprites.powerup import Powerup  # Import Powerup for powerup spawning

class Rabbit(pygame.sprite.Sprite):
    def check_ammo_type(self, ammo_type):
        """
        Only allow 'carrot' ammo type to hit the rabbit.
        All other ammo should pass through.
        """
        return ammo_type == 'carrot'  # Only 'carrot' affects rabbit

    def __init__(self, image_path):
        super().__init__()
        try:
            self.image = pygame.image.load(image_path).convert_alpha()
        except pygame.error as e:
            print(f"Unable to load rabbit image at {image_path}: {e}")
            pygame.quit()
            sys.exit()
        self.image = pygame.transform.scale(self.image, (40, 40))
        self.x = 820  # Start off-screen on the right
        self.y = 90
        self.vx = random.choice([40, 80])  # Set speed, with random choices
        self.vy = -10  # Initial upward speed for bouncing
        self.gravity = 3.5  # Gravity effect for bouncing
        self.initial_y = self.y
        self.bouncing = True
        self.hit = False
        self.vibrate_timer = 0
        self.direction = -1  # Move left initially
        sound_path = os.path.join("D:/Projects/FoodThrowGame2/sound", "eat.mp3")
        try:
            self.eat_sound = pygame.mixer.Sound(sound_path)
        except pygame.error as e:
            print(f"Unable to load sound at {sound_path}: {e}")
            self.eat_sound = None
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
        self.immune = False
        self.fed = False
        self.angry = False
        self.can_drop_powerup = True  # Flag to allow or prevent powerup drops

    def update(self, dt):
        if self.hit and self.vibrate_timer > 0 and not self.angry:
            if int(self.vibrate_timer * 10) % 2 == 0:
                self.y += 2
            else:
                self.y -= 2
            self.vibrate_timer -= dt
            if self.vibrate_timer <= 0:
                self.direction = 1
                self.immune = True
                self.fed = True  # Flag the rabbit as fed
                self.y = self.initial_y
                if self.eat_sound:
                    self.eat_sound.stop()
                self.can_drop_powerup = False  # Prevent further powerup drops
        else:
            self.x += self.vx * dt * self.direction
            self.bounce_logic(dt)

            # Check if the rabbit has stopped moving left
            if self.x < 0 and self.direction == -1:
                self.direction = 1
                self.angry = True
                self.can_drop_powerup = False  # Prevent any further powerup drops
            elif self.x > 800 and self.direction == 1:
                self.reset()

        self.rect.topleft = (self.x, self.y)

    def bounce_logic(self, dt):
        self.vy += self.gravity * dt
        self.y += self.vy * dt
        if self.y >= self.initial_y:
            self.y = self.initial_y
            self.vy = -10

    def reset(self):
        """Reset rabbit to starting conditions when reaching the right edge."""
        self.hit = False
        self.immune = False
        self.fed = False
        self.angry = False
        self.y = self.initial_y
        self.x = 820
        self.vy = -10
        self.direction = -1
        self.can_drop_powerup = True  # Reset drop eligibility on respawn

    def draw(self, screen, bushes):
        rabbit_rect = pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())
        for bush in bushes:
            if rabbit_rect.colliderect(bush):
                visible_height = bush.top - rabbit_rect.top
                if visible_height > 0:
                    visible_rect = pygame.Rect(self.x, self.y, self.image.get_width(), visible_height)
                    screen.blit(self.image.subsurface(0, 0, self.image.get_width(), visible_height), (self.x, self.y))
                    return
        screen.blit(self.image, (self.x, self.y))

    def on_hit(self):
        """Handle rabbit behavior when hit by ammo."""
        if not self.immune and not self.hit and self.direction == -1:
            self.hit = True
            self.vibrate_timer = 1.5  # Set vibration duration
            if self.eat_sound:
                self.eat_sound.play()
            return self.drop_powerup()  # Drop powerup if eligible
        return None

    def blocks_ammo(self):
        return self.angry  # Angry rabbits block ammo; fed rabbits do not

    def drop_powerup(self):
        """Rabbit drops a berry powerup 50% of the time if eligible."""
        powerup_image_path = os.path.join("D:/Projects/FoodThrowGame2/art", "berry.png")
        if self.direction == -1 and self.can_drop_powerup:
            if random.randint(1, 100) <= 50:  # 50% chance for berry ammo
                return Powerup("berry", self.rect.centerx, self.rect.centery, powerup_image_path)
        return None  # No drop if rabbit is not eligible or moving to the right
