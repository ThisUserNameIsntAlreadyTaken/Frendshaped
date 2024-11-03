import sys
import pygame
import os
import time
import random
import math
from Sprites.rabbit import Rabbit
from Sprites.fox import Fox
from Sprites.bear import Bear
from Sprites.powerup import Powerup

# Initialize Pygame
pygame.init()

# Constants
GAME_WIDTH, GAME_HEIGHT = 800, 600  # Internal resolution
FPS = 60
hit_flash_duration = 0.2  # Flash duration in seconds (moved to global scope)

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# Initialize display
is_fullscreen = False  # Flag to track full-screen mode
display_flags = pygame.RESIZABLE
display_surface = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT), display_flags)
pygame.display.set_caption("Level 1")

# Create game surface for internal rendering
game_surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))

# Clock for controlling frame rate
clock = pygame.time.Clock()

# Root directory for assets
root_dir = "D:/Projects/FoodThrowGame2"

# Define news headlines for the news ticker
news_headlines = [
    
    "- Community Garden Feeds Hundreds in Need -"
    "- Wild Life Thrives in Protected Areas -"
    "- Volunteers Restore Historic Park for All -"
    "- Solar Bike Path Unveiled in Beary Woods -"
    "- New Paid Parental Leave Policy for Bears is Welcomed -"
    "- Festival Highlights Different Cuisine -"
    "- Farm Donates Unlimited Carrots to Feed Rabbits -"
]

# Powerup images (for permanent HUD, excluding honey)
try:
    powerup_images = {
        "apple": pygame.image.load(os.path.join(root_dir, "art", "apple.png")).convert_alpha(),
        "banana": pygame.image.load(os.path.join(root_dir, "art", "banana.png")).convert_alpha(),
        "pineapple": pygame.image.load(os.path.join(root_dir, "art", "pineapple.png")).convert_alpha()
    }
except pygame.error as e:
    print(f"Unable to load powerup images: {e}")
    pygame.quit()
    sys.exit()

# Resize powerup images to fit HUD boxes
for key in powerup_images:
    powerup_images[key] = pygame.transform.scale(powerup_images[key], (40, 40))

# Clock sprite class
class ClockSprite(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        clock_image_path = os.path.join(root_dir, "art", "clock.png")
        try:
            self.image = pygame.image.load(clock_image_path).convert_alpha()
        except pygame.error as e:
            print(f"Unable to load clock image at {clock_image_path}: {e}")
            pygame.quit()
            sys.exit()
        self.image = pygame.transform.scale(self.image, (40, 40))
        self.rect = self.image.get_rect(center=(x, y))

# Ammo class
class Ammo:
    def __init__(self, x, y, image, bushes, is_berry=False, speed=2, angle=0):
        self.x = x
        self.y = y
        self.image = image
        self.speed = speed
        self.angle = math.radians(angle)
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
        self.is_berry = is_berry
        self.bushes = bushes
        if self.is_berry:
            self.adjust_hitbox()

    def adjust_hitbox(self):
        for bush in self.bushes:
            if bush.top > self.y:
                self.rect.height = bush.top - self.y
                break

    def update(self):
        self.x += self.speed * math.cos(self.angle)
        self.y -= self.speed * math.sin(self.angle)
        self.rect.x = self.x
        self.rect.y = self.y

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

# Player class
class Player:
    def __init__(self, x, image_path):
        self.original_image_path = image_path
        self.throwing_image_path = os.path.join(root_dir, "art", "player2.png")
        try:
            self.image = pygame.image.load(self.original_image_path).convert_alpha()
        except pygame.error as e:
            print(f"Unable to load player image at {self.original_image_path}: {e}")
            pygame.quit()
            sys.exit()
        self.image = pygame.transform.scale(self.image, (60, 60))
        self.x = x
        self.bushes = [52, 196, 333, 483]
        self.bush_index = 0
        self.y = self.bushes[self.bush_index]
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
        self.is_throwing = False
        self.base_speed = 5
        self.speed = self.base_speed
        self.cooldown = 0  # Cooldown timer

    def increase_speed(self):
        self.speed = self.base_speed * 2

    def reset_speed(self):
        self.speed = self.base_speed

    def move_up(self):
        if self.bush_index > 0:
            self.bush_index -= 1
            self.y = self.bushes[self.bush_index]
            self.rect.topleft = (self.x, self.y)

    def move_down(self):
        if self.bush_index < len(self.bushes) - 1:
            self.bush_index += 1
            self.y = self.bushes[self.bush_index]
            self.rect.topleft = (self.x, self.y)

    def throw_ammo(self):
        if not self.is_throwing:
            try:
                self.image = pygame.image.load(self.throwing_image_path).convert_alpha()
            except pygame.error as e:
                print(f"Unable to load throwing player image at {self.throwing_image_path}: {e}")
                pygame.quit()
                sys.exit()
            self.image = pygame.transform.scale(self.image, (60, 60))
            self.rect = self.image.get_rect(topleft=(self.x, self.y))
            self.is_throwing = True
            pygame.time.set_timer(pygame.USEREVENT + 1, 500)

    def reset_sprite(self):
        try:
            self.image = pygame.image.load(self.original_image_path).convert_alpha()
        except pygame.error as e:
            print(f"Unable to load player image at {self.original_image_path}: {e}")
            pygame.quit()
            sys.exit()
        self.image = pygame.transform.scale(self.image, (60, 60))
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
        self.is_throwing = False

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

# Function to toggle full-screen mode
def toggle_fullscreen():
    global is_fullscreen, display_surface
    is_fullscreen = not is_fullscreen
    if is_fullscreen:
        # Switch to full-screen mode
        display_surface = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    else:
        # Switch back to windowed mode
        display_surface = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT), pygame.RESIZABLE)

# Function to draw Ammo HUD on top left
def draw_ammo_hud(screen, ammo_counts, ammo_sprites, selected_ammo):
    box_size = (80, 50)
    box_padding = 10  # Adjusted padding for consistent spacing
    start_x = 10
    start_y = 10
    font = pygame.font.SysFont(None, 30)
    shades_of_dark_brown = [(101, 67, 33), (139, 69, 19), (160, 82, 45)]

    for i in range(3):
        box_color = shades_of_dark_brown[i] if i == selected_ammo else BLACK
        box_rect = pygame.Rect(start_x + (box_size[0] + box_padding) * i, start_y, *box_size)
        pygame.draw.rect(screen, box_color, box_rect)
        pygame.draw.rect(screen, WHITE, box_rect, 3)

        if i > 0:
            ammo_count_text = font.render(str(ammo_counts[i]), True, WHITE)
            text_rect = ammo_count_text.get_rect(center=(box_rect.x + 20, box_rect.y + box_size[1] // 2))
            screen.blit(ammo_count_text, text_rect)
            sprite = ammo_sprites[i]
            sprite_rect = sprite.get_rect(center=(box_rect.x + 60, box_rect.y + box_size[1] // 2))
        else:
            sprite = ammo_sprites[i]
            sprite_rect = sprite.get_rect(center=(box_rect.x + box_size[0] // 2, box_rect.y + box_size[1] // 2))
        screen.blit(sprite, sprite_rect)

# Function to draw Permanent Powerup HUD on top right
def draw_permanent_powerup_hud(screen, powerup_counts):
    box_size = (80, 50)
    box_padding = 10  # Adjusted padding for consistent spacing
    font = pygame.font.SysFont(None, 30)
    start_x = GAME_WIDTH - box_size[0] - 10
    start_y = 10
    powerup_order = ["apple", "banana", "pineapple"]

    for i, powerup_type in enumerate(powerup_order):
        # Determine outline color based on powerup activation
        outline_color = RED if powerup_counts[powerup_type] > 0 else WHITE

        box_rect = pygame.Rect(start_x - (box_size[0] + box_padding) * i, start_y, *box_size)
        pygame.draw.rect(screen, BLACK, box_rect)
        pygame.draw.rect(screen, outline_color, box_rect, 2)  # Dynamic outline color

        sprite = powerup_images[powerup_type]
        sprite_rect = sprite.get_rect(center=(box_rect.x + 20, box_rect.y + box_size[1] // 2))
        screen.blit(sprite, sprite_rect)

        counter = max(0, powerup_counts[powerup_type])
        counter_text = font.render(str(int(counter)), True, WHITE)
        counter_rect = counter_text.get_rect(center=(box_rect.x + 60, box_rect.y + box_size[1] // 2))
        screen.blit(counter_text, counter_rect)

def draw_bear_hud(screen, health, bear_hit_timer, hud_rect):
    hud_width, hud_height = hud_rect.width, hud_rect.height

    # Create a list of yellow shades for flashing effect
    yellow_shades = [(255, 255, 0), (255, 223, 0), (255, 191, 0), (255, 159, 0)]
    num_shades = len(yellow_shades)

    # Determine the current shade based on bear_hit_timer
    if bear_hit_timer > 0:
        # Calculate the index of the shade to use
        index = int((hit_flash_duration - bear_hit_timer) / hit_flash_duration * num_shades)
        index = min(index, num_shades - 1)
        hud_color = yellow_shades[index]
    else:
        hud_color = BLACK

    pygame.draw.rect(screen, hud_color, hud_rect)
    pygame.draw.rect(screen, RED, hud_rect, 2)  # Red outline

    max_health_width = hud_width - 10
    health_width = int(max_health_width * health / 100)
    pygame.draw.rect(screen, GREEN, (hud_rect.x + 5, hud_rect.y + 10, health_width, 20))
    pygame.draw.rect(screen, RED, (hud_rect.x + 5 + health_width, hud_rect.y + 10, max_health_width - health_width, 20))

    bear_sprite_path = os.path.join(root_dir, "art", "bear.png")
    try:
        bear_sprite = pygame.image.load(bear_sprite_path).convert_alpha()
    except pygame.error as e:
        print(f"Unable to load bear image at {bear_sprite_path}: {e}")
        pygame.quit()
        sys.exit()
    bear_sprite = pygame.transform.scale(bear_sprite, (30, 30))
    screen.blit(bear_sprite, (hud_rect.x + hud_width - 40, hud_rect.y + 10))

# Function to draw News Ticker
def draw_news_ticker(screen, headlines, font, color, hud_rect, scroll_speed=2):
    """
    Draws a scrolling news ticker with provided headlines.

    :param screen: The main game screen.
    :param headlines: A list of news headlines to display.
    :param font: The font object for rendering text.
    :param color: The color of the text.
    :param hud_rect: The pygame.Rect object defining the HUD area.
    :param scroll_speed: Speed at which the text scrolls.
    """
    # Initialize static variables
    if not hasattr(draw_news_ticker, "current_headline"):
        draw_news_ticker.current_headline = 0
        draw_news_ticker.x = hud_rect.x + hud_rect.width
        draw_news_ticker.y = hud_rect.y + (hud_rect.height - font.get_height()) // 2
        draw_news_ticker.hud_surface = pygame.Surface((hud_rect.width, hud_rect.height), pygame.SRCALPHA)
        draw_news_ticker.hud_surface.fill((0, 0, 0, 150))  # Semi-transparent black
        pygame.draw.rect(draw_news_ticker.hud_surface, RED, (0, 0, hud_rect.width, hud_rect.height), 2)  # Red outline

    # Get the current headline
    headline = headlines[draw_news_ticker.current_headline]
    headline_surface = font.render(headline, True, color)
    headline_width = headline_surface.get_width()

    # Clear the HUD surface
    draw_news_ticker.hud_surface.fill((0, 0, 0, 150))  # Semi-transparent black
    pygame.draw.rect(draw_news_ticker.hud_surface, RED, (0, 0, hud_rect.width, hud_rect.height), 2)  # Red outline

    # Blit the headline onto the HUD surface
    draw_news_ticker.hud_surface.blit(headline_surface, (draw_news_ticker.x - hud_rect.x, draw_news_ticker.y - hud_rect.y))

    # Blit the HUD surface onto the main screen
    screen.blit(draw_news_ticker.hud_surface, (hud_rect.x, hud_rect.y))

    # Move the headline to the left
    draw_news_ticker.x -= scroll_speed

    # If the headline has moved off the screen, move to the next headline
    if draw_news_ticker.x < hud_rect.x - headline_width:
        draw_news_ticker.current_headline = (draw_news_ticker.current_headline + 1) % len(headlines)
        draw_news_ticker.x = hud_rect.x + hud_rect.width

# Function to display the swirling effect
def display_swirling_effect():
    swirl_duration = 2.0  # Duration in seconds
    start_time = time.time()
    swirl_image = game_surface.copy()

    while True:
        elapsed_time = time.time() - start_time
        if elapsed_time > swirl_duration:
            break

        angle = (elapsed_time / swirl_duration) * 360 * 3  # Rotate multiple times
        scaled_surface = pygame.transform.rotozoom(swirl_image, angle, 1 - elapsed_time / swirl_duration)
        rect = scaled_surface.get_rect(center=(GAME_WIDTH // 2, GAME_HEIGHT // 2))

        game_surface.fill(BLACK)
        game_surface.blit(scaled_surface, rect)

        # Blit to display_surface with scaling if in full-screen
        if is_fullscreen:
            # Get current display resolution
            display_info = pygame.display.Info()
            display_width, display_height = display_info.current_w, display_info.current_h

            # Calculate scaling while preserving aspect ratio
            scale_x = display_width / GAME_WIDTH
            scale_y = display_height / GAME_HEIGHT
            scale = min(scale_x, scale_y)

            # New size
            new_width = int(GAME_WIDTH * scale)
            new_height = int(GAME_HEIGHT * scale)

            # Scale the game_surface
            scaled_display_surface = pygame.transform.scale(game_surface, (new_width, new_height))

            # Calculate position to center
            x_pos = (display_width - new_width) // 2
            y_pos = (display_height - new_height) // 2

            # Fill display_surface
            display_surface.fill(BLACK)

            # Blit scaled_surface
            display_surface.blit(scaled_display_surface, (x_pos, y_pos))
        else:
            # Blit game_surface directly to display_surface
            display_surface.blit(game_surface, (0, 0))

        pygame.display.flip()
        clock.tick(FPS)

# Function to display the Game Over screen
def display_game_over_screen():
    # Load game over background image
    gameover_background_path = os.path.join(root_dir, "art", "gameover.png")
    try:
        gameover_background = pygame.image.load(gameover_background_path).convert_alpha()
        gameover_background = pygame.transform.scale(gameover_background, (GAME_WIDTH, GAME_HEIGHT))
    except pygame.error as e:
        print(f"Unable to load gameover background image at {gameover_background_path}: {e}")
        # If background image is essential, exit; otherwise, proceed without it
        gameover_background = None

    # Define fonts
    try:
        font_large = pygame.font.SysFont(None, 80, bold=True)
        font_small = pygame.font.SysFont(None, 40)
    except Exception as e:
        print(f"Font initialization error: {e}")
        pygame.quit()
        sys.exit()

    # Define messages
    press_key_message = "PRESS ANY KEY TO RESTART"
    game_over_message = "GAME OVER"

    # Render texts
    game_over_surface = font_large.render(game_over_message, True, RED)
    press_key_surface = font_small.render(press_key_message, True, WHITE)

    # Get text rectangles
    game_over_rect = game_over_surface.get_rect()
    press_key_rect = press_key_surface.get_rect(center=(GAME_WIDTH // 2, GAME_HEIGHT - 100))

    # Initialize position for dancing "GAME OVER" text
    game_over_rect.center = (GAME_WIDTH // 2, GAME_HEIGHT // 2)

    # Dancing parameters
    dance_direction = 1  # 1 for right, -1 for left
    dance_speed = 2  # Pixels per frame
    dance_range = 50  # Pixels to move left and right from center
    dance_timer = 0  # To track movement direction

    # Flashing parameters for "PRESS ANY KEY TO RESTART" text
    flash_timer = 0
    flash_interval = 30  # Frames between color changes
    color_toggle = [WHITE, (200, 200, 200), (150, 150, 150)]
    color_index = 0

    # Load and play the game over music (Track 7)
    track7_path = os.path.join(root_dir, "sound", "track7.mp3")
    try:
        pygame.mixer.music.stop()  # Stop any current music
        pygame.mixer.music.load(track7_path)
        pygame.mixer.music.play(-1)  # Loop the track
    except pygame.error as e:
        print(f"Unable to load or play music at {track7_path}: {e}")
        # Proceed without music if not essential

    # Initialize delay variables
    delay = 1.0  # 1 second delay before allowing key presses
    delay_start_time = time.time()
    key_press_allowed = False

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and key_press_allowed:
                # Restart the level when any key is pressed
                pygame.mixer.music.stop()  # Stop game over music
                running = False
                start_level()  # Call the function that starts Level 1
                return  # Exit this function after starting the level

        # Handle 1-second delay before allowing key presses
        current_time = time.time()
        if not key_press_allowed and current_time - delay_start_time >= delay:
            key_press_allowed = True

        # Update "GAME OVER" text position for dancing effect
        if dance_timer < dance_range and dance_direction == 1:
            game_over_rect.x += dance_speed
            dance_timer += dance_speed
            if dance_timer >= dance_range:
                dance_direction = -1
        elif dance_timer > -dance_range and dance_direction == -1:
            game_over_rect.x -= dance_speed
            dance_timer -= dance_speed
            if dance_timer <= -dance_range:
                dance_direction = 1

        # Update flashing effect
        flash_timer += 1
        if flash_timer >= flash_interval:
            flash_timer = 0
            color_index = (color_index + 1) % len(color_toggle)
            press_key_surface = font_small.render(press_key_message, True, color_toggle[color_index])

        # Draw background
        if gameover_background:
            game_surface.blit(gameover_background, (0, 0))
        else:
            game_surface.fill(BLACK)  # Fallback to black if no background image

        # Draw "GAME OVER" text
        game_surface.blit(game_over_surface, game_over_rect)

        # Draw "PRESS ANY KEY TO RESTART" text
        game_surface.blit(press_key_surface, press_key_rect)

        # Blit to display_surface with scaling if in full-screen
        if is_fullscreen:
            # Get current display resolution
            display_info = pygame.display.Info()
            display_width, display_height = display_info.current_w, display_info.current_h

            # Calculate scaling while preserving aspect ratio
            scale_x = display_width / GAME_WIDTH
            scale_y = display_height / GAME_HEIGHT
            scale = min(scale_x, scale_y)

            # New size
            new_width = int(GAME_WIDTH * scale)
            new_height = int(GAME_HEIGHT * scale)

            # Scale the game_surface
            scaled_surface = pygame.transform.scale(game_surface, (new_width, new_height))

            # Calculate position to center
            x_pos = (display_width - new_width) // 2
            y_pos = (display_height - new_height) // 2

            # Fill display_surface
            display_surface.fill(BLACK)

            # Blit scaled_surface
            display_surface.blit(scaled_surface, (x_pos, y_pos))
        else:
            # Blit game_surface directly to display_surface
            display_surface.blit(game_surface, (0, 0))

        # Update the display
        pygame.display.flip()
        clock.tick(FPS)

# Function to display the Level 1 Complete screen
def display_level1_complete_screen():
    # Load level 1 complete assets
    level1complete_image_path = os.path.join(root_dir, "art", "L1C.png")
    try:
        level1complete_image = pygame.image.load(level1complete_image_path).convert_alpha()
        level1complete_image = pygame.transform.scale(level1complete_image, (GAME_WIDTH, GAME_HEIGHT))
    except pygame.error as e:
        print(f"Unable to load Level 1 Complete image at {level1complete_image_path}: {e}")
        pygame.quit()
        sys.exit()

    # Stop any current music and play track8.mp3
    track8_path = os.path.join(root_dir, "sound", "track8.mp3")
    try:
        pygame.mixer.music.stop()
        pygame.mixer.music.load(track8_path)
        pygame.mixer.music.play(-1)
    except pygame.error as e:
        print(f"Unable to load or play music at {track8_path}: {e}")
        # Proceed without music if not essential

    font_large = pygame.font.SysFont(None, 50, bold=True)
    font_small = pygame.font.SysFont(None, 40)
    text_message = "CONGRATULATIONS! LEVEL 1 COMPLETE"
    press_key_message = "PRESS ANY KEY TO CONTINUE"

    # Colors
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)

    # Flashing effect for "PRESS ANY KEY TO CONTINUE" text
    flash_timer = 0
    flash_interval = 30  # Frames between color changes
    color_toggle = [WHITE, (200, 200, 200), (150, 150, 150)]
    color_index = 0

    # Initialize delay variables
    delay = 1.0  # 1 second delay
    delay_start_time = time.time()
    key_press_allowed = False

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and key_press_allowed:
                # Load level2.py
                try:
                    import level2  # Assuming level2.py has a start_level2() function
                except ImportError as e:
                    print(f"Unable to load level2.py: {e}")
                    pygame.quit()
                    sys.exit()
                running = False
                level2.start_level2()  # Call the function that starts level 2
                return  # Exit the function after starting level 2

        # Handle 1-second delay before allowing key presses
        current_time = time.time()
        if not key_press_allowed and current_time - delay_start_time >= delay:
            key_press_allowed = True

        # Update flashing effect
        if key_press_allowed:
            flash_timer += 1
            if flash_timer >= flash_interval:
                flash_timer = 0
                color_index = (color_index + 1) % len(color_toggle)
                press_key_surface = font_small.render(press_key_message, True, color_toggle[color_index])

        # Draw background
        if level1complete_image:
            game_surface.blit(level1complete_image, (0, 0))
        else:
            game_surface.fill(BLACK)  # Fallback to black if no image

        # Render texts
        text_surface = font_large.render(text_message, True, WHITE)
        press_key_surface = font_small.render(press_key_message, True, color_toggle[color_index])

        # Get text rectangles
        text_rect = text_surface.get_rect(center=(GAME_WIDTH // 2, GAME_HEIGHT // 2 - 50))
        press_key_rect = press_key_surface.get_rect(center=(GAME_WIDTH // 2, GAME_HEIGHT - 100))

        # Draw texts
        game_surface.blit(text_surface, text_rect)
        game_surface.blit(press_key_surface, press_key_rect)

        # Blit to display_surface with scaling if in full-screen
        if is_fullscreen:
            # Get current display resolution
            display_info = pygame.display.Info()
            display_width, display_height = display_info.current_w, display_info.current_h

            # Calculate scaling while preserving aspect ratio
            scale_x = display_width / GAME_WIDTH
            scale_y = display_height / GAME_HEIGHT
            scale = min(scale_x, scale_y)

            # New size
            new_width = int(GAME_WIDTH * scale)
            new_height = int(GAME_HEIGHT * scale)

            # Scale the game_surface
            scaled_surface = pygame.transform.scale(game_surface, (new_width, new_height))

            # Calculate position to center
            x_pos = (display_width - new_width) // 2
            y_pos = (display_height - new_height) // 2

            # Fill display_surface
            display_surface.fill(BLACK)

            # Blit scaled_surface
            display_surface.blit(scaled_surface, (x_pos, y_pos))
        else:
            # Blit game_surface directly to display_surface
            display_surface.blit(game_surface, (0, 0))

        # Update the display
        pygame.display.flip()
        clock.tick(FPS)

# Function to get adjusted mouse position
def get_game_surface_mouse_pos():
    mouse_x, mouse_y = pygame.mouse.get_pos()

    if is_fullscreen:
        # Get current display resolution
        display_info = pygame.display.Info()
        display_width, display_height = display_info.current_w, display_info.current_h

        # Calculate scaling while preserving aspect ratio
        scale_x = display_width / GAME_WIDTH
        scale_y = display_height / GAME_HEIGHT
        scale = min(scale_x, scale_y)

        # New size
        new_width = int(GAME_WIDTH * scale)
        new_height = int(GAME_HEIGHT * scale)

        # Calculate position to center
        x_pos = (display_width - new_width) // 2
        y_pos = (display_height - new_height) // 2

        # Adjust mouse position
        adjusted_x = (mouse_x - x_pos) / scale
        adjusted_y = (mouse_y - y_pos) / scale

        # Ensure the adjusted coordinates are within game_surface bounds
        adjusted_x = max(0, min(adjusted_x, GAME_WIDTH))
        adjusted_y = max(0, min(adjusted_y, GAME_HEIGHT))

        return adjusted_x, adjusted_y
    else:
        # Mouse coordinates are already in game_surface coordinates
        return mouse_x, mouse_y

# Function to start the level
def start_level():
    # Stop current music and play track2.mp3
    track2_path = os.path.join(root_dir, "sound", "track2.mp3")
    try:
        pygame.mixer.music.stop()  # Stop any current music
        pygame.mixer.music.load(track2_path)
        pygame.mixer.music.play(-1)  # Loop the track
    except pygame.error as e:
        print(f"Unable to load or play music at {track2_path}: {e}")
        # Proceed without music if not essential

    background_image_path = os.path.join(root_dir, "art", "background1.png")
    try:
        background_image = pygame.image.load(background_image_path).convert_alpha()
        background_image = pygame.transform.scale(background_image, (GAME_WIDTH, GAME_HEIGHT))
    except pygame.error as e:
        print(f"Unable to load background image at {background_image_path}: {e}")
        pygame.quit()
        sys.exit()

    player_image_path = os.path.join(root_dir, "art", "player1.png")
    try:
        player = Player(40, player_image_path)
    except pygame.error as e:
        print(f"Unable to load player image at {player_image_path}: {e}")
        pygame.quit()
        sys.exit()

    # Initialize Ammo
    carrot_image_path = os.path.join(root_dir, "art", "carrot.png")
    try:
        carrot_image = pygame.image.load(carrot_image_path).convert_alpha()
    except pygame.error as e:
        print(f"Unable to load carrot image at {carrot_image_path}: {e}")
        pygame.quit()
        sys.exit()
    carrot_image = pygame.transform.scale(carrot_image, (25, 25))

    berry_image_path = os.path.join(root_dir, "art", "berry.png")
    try:
        berry_image = pygame.image.load(berry_image_path).convert_alpha()
    except pygame.error as e:
        print(f"Unable to load berry image at {berry_image_path}: {e}")
        pygame.quit()
        sys.exit()
    berry_image = pygame.transform.scale(berry_image, (25, 25))

    honey_image_path = os.path.join(root_dir, "art", "honey.png")
    try:
        honey_image = pygame.image.load(honey_image_path).convert_alpha()
    except pygame.error as e:
        print(f"Unable to load honey image at {honey_image_path}: {e}")
        pygame.quit()
        sys.exit()
    honey_image = pygame.transform.scale(honey_image, (25, 25))

    ammo_counts = [5, 5, 0]  # Initial ammo counts for carrot, berry, and honey
    ammo_sprites = [carrot_image, berry_image, honey_image]
    selected_ammo = 0
    fired_ammo = []
    last_fire_time = 0
    rabbit_spawn_timer = 0.75  # Halved to double the spawn rate
    max_rabbits = 10  # Increased to allow up to 10 rabbits on screen
    rabbits = []
    fox_spawn_timer = 0.75
    foxes = []
    bear_spawned = False
    bear_health = 100

    bear_hit_timer = 0  # Timer for HUD flash effect on hit
    

    bushes = [
        pygame.Rect(0, 113, GAME_WIDTH, 37),
        pygame.Rect(0, 256, GAME_WIDTH, 37),
        pygame.Rect(0, 393, GAME_WIDTH, 37),
        pygame.Rect(0, 543, GAME_WIDTH, 37)
    ]

    rabbit_spawn_positions = [90, 235, 370, 520]
    fox_spawn_positions = [113, 256, 393, 543]

    powerups = pygame.sprite.Group()
    active_powerups = pygame.sprite.Group()
    clocks = pygame.sprite.Group()  # Group to manage clock sprites
    powerup_counts = {"apple": 0, "banana": 0, "pineapple": 0}

    # Initialize font for the news ticker
    ticker_font = pygame.font.SysFont("Arial", 24, bold=True)
    ticker_color = RED  # Mechanical red letters

    # Define the HUD rectangle (where the bear HUD appears)
    hud_height = 50
    hud_width = 160
    left_hud_x = 10 + (3 * (80 + 10))  # Calculate total width of ammo HUD
    right_hud_x = GAME_WIDTH - 10 - (3 * (80 + 10))  # Calculate total width of powerup HUD
    hud_x = (left_hud_x + right_hud_x - hud_width) // 2  # Centered between HUDs
    hud_y = 10
    hud_rect = pygame.Rect(hud_x, hud_y, hud_width, hud_height)

    # Scrolling speed for the news ticker
    ticker_scroll_speed = 2

    # Flag to check if clock has been dropped
    clock_dropped = False

    # Initialize bear spawn timer
    bear_spawn_timer = 30.0  # Initial timer set to 30 seconds (adjust as needed)

    # Main game loop
    running = True
    while running:
        dt = clock.tick(FPS) / 1000  # Delta time in seconds

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                # Detect Alt + Enter
                if event.key == pygame.K_RETURN and (event.mod & pygame.KMOD_ALT):
                    toggle_fullscreen()
                # Optional: Exit full-screen with Escape
                elif event.key == pygame.K_ESCAPE and is_fullscreen:
                    toggle_fullscreen()
                elif event.key == pygame.K_w:
                    player.move_up()
                elif event.key == pygame.K_s:
                    player.move_down()
                elif event.key == pygame.K_a:
                    selected_ammo = (selected_ammo - 1) % 3
                elif event.key == pygame.K_d:
                    selected_ammo = (selected_ammo + 1) % 3
                elif event.key == pygame.K_SPACE:
                    # Fire only if there’s sufficient ammo for the selected type and cooldown is not active
                    if (ammo_counts[selected_ammo] > 0 or selected_ammo == 0) and player.cooldown <= 0:
                        ammo_speed = 2 if powerup_counts["banana"] <= 0 else 6
                        is_berry = selected_ammo == 1  # Index 1 corresponds to berries
                        if powerup_counts["pineapple"] > 0:
                            angles = [0, 45, -45]
                            for angle in angles:
                                ammo = Ammo(player.x + 60, player.y + 20, ammo_sprites[selected_ammo], bushes, is_berry=is_berry, speed=ammo_speed, angle=angle)
                                fired_ammo.append(ammo)
                        else:
                            ammo = Ammo(player.x + 60, player.y + 20, ammo_sprites[selected_ammo], bushes, is_berry=is_berry, speed=ammo_speed)
                            fired_ammo.append(ammo)
                        player.throw_ammo()
                        if selected_ammo != 0:
                            ammo_counts[selected_ammo] -= 1
                        last_fire_time = time.time()

                        # Reset the cooldown
                        player.cooldown = 0.5  # Set cooldown to 0.5 seconds
            elif event.type == pygame.USEREVENT + 1:
                player.reset_sprite()
                pygame.time.set_timer(pygame.USEREVENT + 1, 0)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Use adjusted mouse position for accurate collision detection
                mouse_pos = get_game_surface_mouse_pos()
                # Check for clock sprite clicks
                for clock_sprite in clocks:
                    if clock_sprite.rect.collidepoint(mouse_pos):
                        # Freeze the game
                        running = False

                        # Stop the music
                        pygame.mixer.music.stop()

                        # Display swirling effect
                        display_swirling_effect()

                        # Display level 1 complete screen
                        display_level1_complete_screen()
                        return  # Exit the function after level completion

                # Check for powerup clicks
                for powerup in powerups:
                    if powerup.rect.collidepoint(mouse_pos):
                        if powerup.type == "berry":
                            ammo_counts[1] += 5
                        elif powerup.type == "honey":
                            ammo_counts[2] += 1
                        else:
                            powerup_type = powerup.type
                            if powerup_type in powerup_counts:
                                powerup_counts[powerup_type] += 5
                        powerup.kill()

        # Only update game state if running
        if running:
            # Handle Powerup durations and effects
            for powerup_type in powerup_counts:
                if powerup_counts[powerup_type] > 0:
                    powerup_counts[powerup_type] -= dt
                    if powerup_type == "apple" and powerup_counts["apple"] > 0:
                        for powerup in powerups:
                            direction_x = player.x - powerup.rect.x
                            direction_y = player.y - powerup.rect.y
                            distance = math.sqrt(direction_x**2 + direction_y**2)
                            if distance > 0:
                                move_x = (direction_x / distance) * 5
                                move_y = (direction_y / distance) * 5
                                powerup.rect.x += move_x
                                powerup.rect.y += move_y
                            if powerup.rect.colliderect(player.rect):
                                if powerup.type == "berry":
                                    ammo_counts[1] += 5
                                elif powerup.type == "honey":
                                    ammo_counts[2] += 1
                                else:
                                    powerup_counts[powerup.type] += 5
                                powerup.kill()

            # Render game elements onto game_surface
            game_surface.fill((139, 69, 19))  # Fill with brown color (background)
            game_surface.blit(background_image, (0, 0))  # Draw background image
            player.draw(game_surface)

            # Handle Rabbit Spawning
            if rabbit_spawn_timer <= 0 and len(rabbits) < max_rabbits:
                rabbit_image_path = os.path.join(root_dir, "art", "rabbit.png")
                try:
                    new_rabbit = Rabbit(rabbit_image_path)
                except pygame.error as e:
                    print(f"Unable to load rabbit image at {rabbit_image_path}: {e}")
                    pygame.quit()
                    sys.exit()
                chosen_y = random.choice(rabbit_spawn_positions)
                new_rabbit.y = chosen_y
                new_rabbit.initial_y = chosen_y
                rabbits.append(new_rabbit)
                rabbit_spawn_timer = 0.75  # Reset spawn timer to the new interval
            rabbit_spawn_timer -= dt

            # Handle Fox Spawning
            if fox_spawn_timer <= 0:
                fox_image_path = os.path.join(root_dir, "art", "fox.png")
                try:
                    new_fox = Fox(fox_image_path, random.choice(['upper', 'middle', 'lower', 'bottom']))
                except pygame.error as e:
                    print(f"Unable to load fox image at {fox_image_path}: {e}")
                    pygame.quit()
                    sys.exit()
                foxes.append(new_fox)
                fox_spawn_timer = 0.75  # Reset spawn timer
            fox_spawn_timer -= dt

            # Modified Bear Spawning Logic
            if not bear_spawned:
                bear_spawn_timer -= dt
                if bear_spawn_timer <= 0:
                    honey_count = ammo_counts[2]  # Use the current honey ammo count
                    spawn_chance = min(honey_count * 20, 100)  # 20% per honey, up to 100%

                    # Generate a random number to determine if the bear spawns
                    random_number = random.randint(1, 100)
                    print(f"Bear spawn attempt: Spawn chance = {spawn_chance}%, Random number = {random_number}")

                    if random_number <= spawn_chance:
                        bear_image_path = os.path.join(root_dir, "art", "bear.png")
                        try:
                            bear = Bear(bear_image_path, random.choice(['upper', 'middle', 'lower', 'bottom']))
                        except pygame.error as e:
                            print(f"Unable to load bear image at {bear_image_path}: {e}")
                            pygame.quit()
                            sys.exit()
                        bear_spawned = True
                        pygame.mixer.music.stop()
                        track6_path = os.path.join(root_dir, "sound", "track6.mp3")
                        try:
                            pygame.mixer.music.load(track6_path)
                            pygame.mixer.music.play(-1)
                        except pygame.error as e:
                            print(f"Unable to load or play music at {track6_path}: {e}")
                            pygame.quit()
                            sys.exit()
                    else:
                        print("Bear did not spawn this attempt.")

                    # Reset the bear spawn timer for the next attempt
                    bear_spawn_timer = 30.0  # Set to 30 seconds

            if bear_spawned:
                bear.update(dt)
                bear.draw(game_surface, bushes)
                draw_bear_hud(game_surface, bear.health, bear_hit_timer, hud_rect)
                bear_health = bear.health

                if bear_hit_timer > 0:
                    bear_hit_timer -= dt

                # Check if bear reaches or passes the player's x-coordinate for game over
                if bear.rect.x <= player.rect.x:
                    # Display game over screen
                    running = False  # Exit the game loop
                    pygame.time.wait(1000)  # Freeze for 1 second
                    display_game_over_screen()  # Call the game over screen function
                    return  # Exit the function after game over

                # Check if bear's health has reached 0
                if bear_health <= 0 and not clock_dropped:
                    # Stop bear-related music and resume track2.mp3
                    pygame.mixer.music.stop()
                    try:
                        track2_path = os.path.join(root_dir, "sound", "track2.mp3")
                        pygame.mixer.music.load(track2_path)
                        pygame.mixer.music.play(-1)
                    except pygame.error as e:
                        print(f"Unable to load or play music at {track2_path}: {e}")
                        pygame.quit()
                        sys.exit()

                    # Remove bear HUD by resetting bear_spawned and hiding bear HUD
                    bear_spawned = False

                    # Drop the clock sprite at bear's last position
                    clock_sprite = ClockSprite(bear.rect.x, bear.rect.y)
                    clocks.add(clock_sprite)

                    clock_dropped = True  # Ensure clock is dropped only once

                # Decrease bear_hit_timer
                if bear_hit_timer > 0:
                    bear_hit_timer -= dt
            else:
                # Draw the news ticker when the bear HUD is not active and game is not complete
                if not clock_dropped:
                    draw_news_ticker(game_surface, news_headlines, ticker_font, ticker_color, hud_rect, scroll_speed=ticker_scroll_speed)

            # Update and draw Rabbits
            for rabbit in rabbits[:]:
                rabbit.update(dt)
                rabbit.draw(game_surface, bushes)
                if not rabbit.fed:  # Only check collision if rabbit is not fed
                    for ammo in fired_ammo[:]:
                        # Only process collision if the ammo is not honey
                        if selected_ammo == 0 and hasattr(rabbit, 'check_ammo_type') and rabbit.check_ammo_type("carrot") and ammo.rect.colliderect(rabbit.rect):
                            rabbit.on_hit()
                            powerup = rabbit.drop_powerup()
                            if powerup:
                                powerups.add(powerup)
                            fired_ammo.remove(ammo)
                            break
                if rabbit.x < -40 or rabbit.x > GAME_WIDTH + 40:
                    rabbits.remove(rabbit)

            # Update and draw Foxes
            for fox in foxes[:]:
                fox.update(dt)
                fox.draw(game_surface, bushes)
                if not fox.is_fed:  # Only check collision if fox is not fed
                    for ammo in fired_ammo[:]:
                        if ammo.is_berry and ammo.rect.colliderect(fox.rect):
                            if not fox.is_hit:
                                powerup = fox.on_hit("berry")
                                if powerup:
                                    powerups.add(powerup)
                                fired_ammo.remove(ammo)
                                break  # Exit the inner loop after handling collision
                if fox.x < -40:
                    foxes.remove(fox)

            # Update and draw Ammo
            for ammo in fired_ammo[:]:
                ammo.update()
                ammo.draw(game_surface)

                # Skip collision detection if the bear is teleporting
                if bear_spawned and ammo.rect.colliderect(bear.rect) and not bear.descending_for_teleport:
                    if ammo.is_berry or selected_ammo == 2:  # Assuming index 2 is honey
                        if ammo.is_berry:
                            bear.on_hit("berry")
                        elif selected_ammo == 2:
                            bear.on_hit("honey")

                        # Play eat3.mp3 sound when the bear is hit
                        sound_path = os.path.join(root_dir, "sound", "eat3.mp3")
                        try:
                            hit_sound = pygame.mixer.Sound(sound_path)
                            hit_sound.play()
                        except pygame.error as e:
                            print(f"Unable to load sound at {sound_path}: {e}")

                        # Set bear_hit_timer for HUD flash
                        bear_hit_timer = hit_flash_duration  # Reset the hit timer

                        fired_ammo.remove(ammo)
                    else:
                        fired_ammo.remove(ammo)
                elif ammo.x > GAME_WIDTH:
                    fired_ammo.remove(ammo)

            # Update and draw Power-ups
            powerups.update()
            active_powerups.update()
            powerups.draw(game_surface)

            # Update and draw Clock sprites
            clocks.update()
            clocks.draw(game_surface)

            # Draw HUDs
            draw_ammo_hud(game_surface, ammo_counts, ammo_sprites, selected_ammo)
            draw_permanent_powerup_hud(game_surface, powerup_counts)

            # Update cooldown timer
            if player.cooldown > 0:
                player.cooldown -= dt  # dt is the frame time

            # Blit to display_surface with scaling if in full-screen
            if is_fullscreen:
                # Get current display resolution
                display_info = pygame.display.Info()
                display_width, display_height = display_info.current_w, display_info.current_h

                # Calculate scaling while preserving aspect ratio
                scale_x = display_width / GAME_WIDTH
                scale_y = display_height / GAME_HEIGHT
                scale = min(scale_x, scale_y)

                # New size
                new_width = int(GAME_WIDTH * scale)
                new_height = int(GAME_HEIGHT * scale)

                # Scale the game_surface
                scaled_surface = pygame.transform.scale(game_surface, (new_width, new_height))

                # Calculate position to center
                x_pos = (display_width - new_width) // 2
                y_pos = (display_height - new_height) // 2

                # Fill display_surface
                display_surface.fill(BLACK)

                # Blit scaled_surface
                display_surface.blit(scaled_surface, (x_pos, y_pos))
            else:
                # Blit game_surface directly to display_surface
                display_surface.blit(game_surface, (0, 0))

            # Update the display
            pygame.display.flip()

# Main game loop function
def main():
    while True:
        start_level()
        # If the level ends (e.g., player loses or completes the level), the loop will continue
        # The display_game_over_screen() is called within start_level() when appropriate

if __name__ == "__main__":
    main()
