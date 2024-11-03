import pygame
import random

class Powerup(pygame.sprite.Sprite):
    def __init__(self, type, x, y, image_path, timer=5):
        super().__init__()
        self.type = type
        self.original_image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.original_image, (50, 50))
        self.rect = self.image.get_rect(center=(x, y))
        self.timer = timer
        self.flash_timer = 3
        self.fade_timer = 2
        self.flashing = True
        self.color_change_interval = 0.1
        self.last_color_change_time = 0
        self.current_shade_index = 0

        self.color_shades = {
            "banana": [(255, 255, 100), (255, 255, 0), (255, 200, 0), (255, 165, 0)],
            "pineapple": [(50, 205, 50), (34, 139, 34), (255, 180, 0), (255, 165, 0)],
            "apple": [(255, 50, 50), (255, 0, 0), (255, 150, 150), (255, 192, 203)],
            "berry": [(255, 70, 70), (255, 0, 0), (200, 0, 0)],
            "honey": [(255, 183, 76), (255, 165, 0), (234, 140, 30), (210, 105, 30)]
        }
        self.shades = self.color_shades.get(self.type, [(255, 255, 255)])

    def activate(self, player, active_powerups):
        existing_powerup = next((p for p in active_powerups if p.type == self.type), None)
        if existing_powerup:
            existing_powerup.timer += 5
        else:
            active_powerups.add(self)
            self.apply_effect(player)

    def apply_effect(self, player):
        if self.type == "banana":
            player.increase_speed()
        elif self.type == "pineapple":
            player.triple_shot = True

    def update(self):
        self.timer -= 1 / 60
        if self.flashing and self.flash_timer > 0:
            self.flash_timer -= 1 / 60
            if self.flash_timer <= 0:
                self.flashing = False
            else:
                self.flash_colors()
        elif self.flash_timer <= 0 and self.fade_timer > 0:
            self.fade_timer -= 1 / 60
            self.fade_out()
        if self.timer <= 0:
            self.deactivate()

    def flash_colors(self):
        if pygame.time.get_ticks() - self.last_color_change_time >= self.color_change_interval * 1000:
            self.image = pygame.transform.scale(self.original_image, (50, 50))
            self.image.fill(self.shades[self.current_shade_index], special_flags=pygame.BLEND_ADD)
            self.current_shade_index = (self.current_shade_index + 1) % len(self.shades)
            self.last_color_change_time = pygame.time.get_ticks()

    def fade_out(self):
        if int(self.fade_timer * 10) % 2 == 0:
            self.image.set_alpha(0)
        else:
            self.image.set_alpha(255)

    def deactivate(self):
        self.kill()

    def click(self, player, hud):
        if self.type == "berry":
            player.berry_ammo += 5
            hud.update_berry_ammo(player.berry_ammo)
        elif self.type == "honey":
            player.honey_ammo += 1
            hud.update_honey_ammo(player.honey_ammo)
        self.kill()

    @staticmethod
    def spawn_random(x_range, y_range, powerup_images):
        type = random.choice(list(powerup_images.keys()))
        x = random.randint(*x_range)
        y = random.randint(*y_range)
        return Powerup(type, x, y, powerup_images[type])

    @staticmethod
    def spawn_weighted_for_fox(x_range, y_range, powerup_images):
        powerup_types = ["banana", "pineapple", "apple", "honey"]
        probabilities = [0.4, 0.3, 0.15, 0.05]  # Drop rates specific to foxes

        # Select a powerup type based on the weighted probabilities
        selected_type = random.choices(powerup_types, probabilities)[0]
        x = random.randint(*x_range)
        y = random.randint(*y_range)

        return Powerup(selected_type, x, y, powerup_images[selected_type])
