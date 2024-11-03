import pygame
import sys
import random
import os
import importlib
from winter import create_snow, update_and_draw_snow, wind_simulator  # Import snow functions from winter.py

class Player:
    def __init__(self, x, y, image_path):
        self.x = x
        self.y = y
        self.image_path = image_path
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (60, 60))  # Adjust size
        self.throwing_image = pygame.image.load(os.path.join("D:/Projects/FoodThrowGame2/art", "player2.png")).convert_alpha()
        self.throwing_image = pygame.transform.scale(self.throwing_image, (60, 60))

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def move_up(self):
        if self.y > 100:
            self.y -= 140

    def move_down(self):
        if self.y < 530:
            self.y += 140

    def throw_ammo(self):
        self.image = self.throwing_image
        pygame.time.set_timer(pygame.USEREVENT, 500)  # Reset after 0.5 seconds

    def reset_sprite(self):
        self.image = pygame.image.load(self.image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (60, 60))

class Ammo:
    def __init__(self, x, y, image):
        self.x = x
        self.y = y
        self.image = image
        self.speed = 1  # Set speed for ammo

    def update(self):
        self.x += self.speed

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

def draw_hud(screen, ammo_counts, ammo_sprites, selected_ammo):
    box_size = (80, 50)
    box_padding = 15
    start_x = 10
    start_y = 10
    font = pygame.font.SysFont(None, 30)
    shades_of_dark_brown = [(101, 67, 33), (139, 69, 19), (160, 82, 45)]

    for i in range(3):
        if i != selected_ammo:
            box_color = (0, 0, 0, 0)
        else:
            box_color = shades_of_dark_brown[i]

        box_rect = pygame.Rect(start_x + (box_size[0] + box_padding) * i, start_y, *box_size)
        pygame.draw.rect(screen, box_color, box_rect)
        pygame.draw.rect(screen, (255, 255, 255), box_rect, 3)

        ammo_count_text = font.render(str(ammo_counts[i]), True, (255, 255, 255))
        text_rect = ammo_count_text.get_rect(center=(box_rect.x + 20, box_rect.y + box_size[1] // 2))
        screen.blit(ammo_count_text, text_rect)

        sprite = ammo_sprites[i]
        sprite_rect = sprite.get_rect(center=(box_rect.x + 60, box_rect.y + box_size[1] // 2))
        screen.blit(sprite, sprite_rect)

def start_level():
    root_dir = "D:/Projects/FoodThrowGame2"
    pygame.init()
    window_size = (800, 600)
    screen = pygame.display.set_mode(window_size)
    pygame.display.set_caption("Level 3")
    brown = (139, 69, 19)
    background_image_path = os.path.join(root_dir, "art", "background3.png")
    background_image = pygame.image.load(background_image_path)
    pygame.mixer.init()
    track4_path = os.path.join(root_dir, "sound", "track4.mp3")
    pygame.mixer.music.load(track4_path)
    pygame.mixer.music.play(-1)

    clock = pygame.time.Clock()
    FPS = 60

    player_image_path = os.path.join(root_dir, "art", "player1.png")
    player = Player(40, 480, player_image_path)

    # Load ammo images
    carrot_image = pygame.image.load(os.path.join(root_dir, "art", "carrot.png")).convert_alpha()
    carrot_image = pygame.transform.scale(carrot_image, (25, 25))

    berry_image = pygame.image.load(os.path.join(root_dir, "art", "berry.png")).convert_alpha()
    berry_image = pygame.transform.scale(berry_image, (25, 25))

    honey_image = pygame.image.load(os.path.join(root_dir, "art", "honey.png")).convert_alpha()
    honey_image = pygame.transform.scale(honey_image, (25, 25))

    # Create initial snowflakes
    snowflakes = []

    # Initialize wind variables
    wind_timer = [random.randint(600, 900)]
    wind_duration = [0]
    wind_speed = [0, random.uniform(1, 2)]

    # Initialize spawn timer for individual snowflakes
    spawn_timer = [random.randint(20, 100)]
    wind_spawn_timer = [120]

    # Ammo and HUD setup
    ammo_counts = [5, 5, 5]
    ammo_sprites = [carrot_image, berry_image, honey_image]
    selected_ammo = 0
    fired_ammo = []

    running = True
    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    player.move_up()
                elif event.key == pygame.K_DOWN:
                    player.move_down()
                elif event.key == pygame.K_LEFT:
                    selected_ammo = (selected_ammo - 1) % 3
                elif event.key == pygame.K_RIGHT:
                    selected_ammo = (selected_ammo + 1) % 3
                elif event.key == pygame.K_SPACE and ammo_counts[selected_ammo] > 0:
                    ammo_image = ammo_sprites[selected_ammo]
                    ammo = Ammo(player.x + 60, player.y + 20, ammo_image)
                    fired_ammo.append(ammo)
                    player.throw_ammo()
                    ammo_counts[selected_ammo] -= 1
                elif event.key == pygame.K_x:
                    pygame.mixer.music.stop()
                    running = False
                    next_level = importlib.import_module('levels.level4')
                    next_level.start_level()

            elif event.type == pygame.USEREVENT:
                player.reset_sprite()

        # Determine if the wind is blowing and update wind speed
        wind_is_blowing = wind_simulator(wind_timer, wind_duration, wind_speed)

        screen.fill(brown)
        screen.blit(background_image, (0, 0))
        player.draw(screen)

        for ammo in fired_ammo:
            ammo.update()
            ammo.draw(screen)

        # Update and draw snowflakes (fixing the missing arguments)
        update_and_draw_snow(screen, snowflakes, root_dir, spawn_timer, wind_is_blowing, wind_speed[0], wind_spawn_timer)

        # Draw the HUD and ammo selection
        draw_hud(screen, ammo_counts, ammo_sprites, selected_ammo)

        pygame.display.flip()

    pygame.quit()
    sys.exit()
