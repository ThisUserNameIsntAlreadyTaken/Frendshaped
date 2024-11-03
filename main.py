import pygame
import sys
import importlib
import os
import configparser

# ---------------------------- #
#        Configuration         #
# ---------------------------- #

# Define the root directory for assets and config file
root_dir = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(root_dir, "config.ini")

# Initialize ConfigParser
config = configparser.ConfigParser()

# Define default configurations
default_config = {
    'KeyBindings': {
        'move_up': 'W',
        'move_down': 'S',
        'select_left_ammo': 'A',
        'select_right_ammo': 'D',
        'throw_carrot': '1',
        'throw_berry': '2',
        'throw_honey': '3',
        'throw_selected_ammo': 'SPACE'
    },
    'Settings': {
        'fullscreen': 'False',
        'music_on': 'True'
    }
}

# Function to load configuration
def load_config():
    if not os.path.exists(CONFIG_FILE):
        # Create config file with default settings
        config.read_dict(default_config)
        with open(CONFIG_FILE, 'w') as configfile:
            config.write(configfile)
    else:
        config.read(CONFIG_FILE)
        # Ensure all default sections and options are present
        updated = False
        for section in default_config:
            if not config.has_section(section):
                config.add_section(section)
                for key, value in default_config[section].items():
                    config.set(section, key, value)
                updated = True
            else:
                for key, value in default_config[section].items():
                    if not config.has_option(section, key):
                        config.set(section, key, value)
                        updated = True
        if updated:
            with open(CONFIG_FILE, 'w') as configfile:
                config.write(configfile)

# Function to save configuration
def save_config():
    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)

# Function to reload settings and keybindings
def reload_settings():
    global MOVE_UP, MOVE_DOWN, SELECT_LEFT_AMMO, SELECT_RIGHT_AMMO
    global THROW_CARROT, THROW_BERRY, THROW_HONEY, THROW_SELECTED_AMMO
    global FULLSCREEN, MUSIC_ON

    MOVE_UP = config.get('KeyBindings', 'move_up').upper()
    MOVE_DOWN = config.get('KeyBindings', 'move_down').upper()
    SELECT_LEFT_AMMO = config.get('KeyBindings', 'select_left_ammo').upper()
    SELECT_RIGHT_AMMO = config.get('KeyBindings', 'select_right_ammo').upper()
    THROW_CARROT = config.get('KeyBindings', 'throw_carrot')
    THROW_BERRY = config.get('KeyBindings', 'throw_berry')
    THROW_HONEY = config.get('KeyBindings', 'throw_honey')
    THROW_SELECTED_AMMO = config.get('KeyBindings', 'throw_selected_ammo').upper()

    FULLSCREEN = config.getboolean('Settings', 'fullscreen')
    MUSIC_ON = config.getboolean('Settings', 'music_on')

# Load and apply configurations at startup
load_config()
reload_settings()

# ---------------------------- #
#        Pygame Setup          #
# ---------------------------- #

# Initialize Pygame
pygame.init()

# Set up the game window
window_size = (800, 600)
if FULLSCREEN:
    screen = pygame.display.set_mode(window_size, pygame.FULLSCREEN)
else:
    screen = pygame.display.set_mode(window_size)
pygame.display.set_caption("Food Throw Game")

# Define FPS and create a clock instance
FPS = 60
clock = pygame.time.Clock()

# Load the splash image from the art folder
splash_image_path = os.path.join(root_dir, "art", "splash.png")
try:
    splash_image = pygame.image.load(splash_image_path).convert_alpha()
    splash_image = pygame.transform.scale(splash_image, window_size)
except pygame.error as e:
    print(f"Unable to load splash image at {splash_image_path}: {e}")
    pygame.quit()
    sys.exit()

# Initialize the mixer for playing sound
pygame.mixer.init()

# Load and play background music from the sound folder
track_path = os.path.join(root_dir, "sound", "track1.mp3")
try:
    pygame.mixer.music.load(track_path)
    if MUSIC_ON:
        pygame.mixer.music.play(-1)  # Loop infinitely
    else:
        pygame.mixer.music.play(-1)
        pygame.mixer.music.pause()
except pygame.error as e:
    print(f"Unable to load or play music at {track_path}: {e}")
    pygame.quit()
    sys.exit()

# Load fruit sprites
fruit_sprites = {
    "carrot": pygame.image.load(os.path.join(root_dir, "art", "carrot.png")).convert_alpha(),
    "berry": pygame.image.load(os.path.join(root_dir, "art", "berry.png")).convert_alpha(),
    "honey": pygame.image.load(os.path.join(root_dir, "art", "honey.png")).convert_alpha()
}

# Scale fruit images for better display in controls (smaller size)
fruit_sprites = {key: pygame.transform.scale(sprite, (30, 30)) for key, sprite in fruit_sprites.items()}

# Font settings for the menu
# Replace 'freesansbold.ttf' with your desired font file if you have a specific font
menu_font = pygame.font.Font(pygame.font.match_font('freesansbold'), 50)  # Larger font for menu options
controls_font = pygame.font.Font(pygame.font.match_font('freesansbold'), 24)  # Smaller font for controls

# Define menu options
menu_options = ["START GAME", "OPTIONS", "EXIT"]
selected_index = 0

# ---------------------------- #
#        Configuration         #
# ---------------------------- #

# Function to update keybinding
def update_keybinding(action, new_key):
    # Prevent duplicate keybindings
    for act in config['KeyBindings']:
        if config.get('KeyBindings', act).upper() == new_key.upper() and act != action:
            print(f"Key '{new_key}' is already assigned to '{act.replace('_', ' ').title()}'. Choose a different key.")
            return False
    config.set('KeyBindings', action, new_key.upper())
    save_config()
    reload_settings()
    return True

# Function to toggle settings
def toggle_setting(setting):
    current_value = config.getboolean('Settings', setting)
    config.set('Settings', setting, str(not current_value))
    save_config()
    reload_settings()
    # Apply changes immediately if necessary
    if setting == 'fullscreen':
        if FULLSCREEN:
            pygame.display.set_mode(window_size, pygame.FULLSCREEN)
        else:
            pygame.display.set_mode(window_size)
    elif setting == 'music_on':
        if MUSIC_ON:
            pygame.mixer.music.unpause()
        else:
            pygame.mixer.music.pause()

# Function to reset configurations to default
def reset_to_defaults():
    config.read_dict(default_config)
    save_config()
    reload_settings()
    print("Configurations have been reset to default values.")

# Function to invert a color (used for flashing effects)
def invert_color(color):
    """Returns the inverted color."""
    return (255 - color[0], 255 - color[1], 255 - color[2])

# ---------------------------- #
#          Menus                #
# ---------------------------- #

# Helper function to render text with outline
def render_text_with_outline(text, font, color, outline_color, scale_factor=1.0):
    text_surface = font.render(text, True, color)
    if scale_factor != 1.0:
        text_surface = pygame.transform.scale(
            text_surface,
            (int(text_surface.get_width() * scale_factor), int(text_surface.get_height() * scale_factor))
        )
    outline_surface = font.render(text, True, outline_color)
    if scale_factor != 1.0:
        outline_surface = pygame.transform.scale(
            outline_surface,
            (int(outline_surface.get_width() * scale_factor), int(outline_surface.get_height() * scale_factor))
        )
    return text_surface, outline_surface

# Helper function to dynamically adjust font size to fit text within a given rectangle
def get_fitting_font(text, font_name, max_width, max_height, initial_size=24, min_size=12):
    font_size = initial_size
    font = pygame.font.Font(pygame.font.match_font(font_name), font_size)
    text_surface = font.render(text, True, (255, 255, 255))
    while (text_surface.get_width() > max_width - 10 or text_surface.get_height() > max_height - 10) and font_size > min_size:
        font_size -= 1
        font = pygame.font.Font(pygame.font.match_font(font_name), font_size)
        text_surface = font.render(text, True, (255, 255, 255))
    return font

# Function to display the start menu
def display_start_menu():
    global selected_index
    running = True
    flash_timer = 0
    flash_interval = 30  # Frames between color toggles
    blue_shades = [
        (0, 0, 255),
        (30, 144, 255),
        (100, 149, 237),
        (70, 130, 180)
    ]
    current_shade = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    selected_index = (selected_index - 1) % len(menu_options)
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    selected_index = (selected_index + 1) % len(menu_options)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if selected_index == 0:  # Start Game
                        try:
                            level1 = importlib.import_module('levels.level1')  # Import levels/level1.py
                            level1.start_level()  # Call the function that starts level 1
                        except Exception as e:
                            print(f"Error loading level1 module: {e}")
                            pygame.quit()
                            sys.exit()
                    elif selected_index == 1:  # Options
                        display_options_menu()
                    elif selected_index == 2:  # Exit
                        pygame.quit()
                        sys.exit()
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                # Define clickable regions for each menu option
                for i, option in enumerate(menu_options):
                    option_rect = pygame.Rect(
                        window_size[0] // 2 - 200, window_size[1] * 0.65 + i * 60 - 25,
                        400, 50
                    )
                    if option_rect.collidepoint(mouse_x, mouse_y):
                        selected_index = i
                        if selected_index == 0:  # Start Game
                            try:
                                level1 = importlib.import_module('levels.level1')
                                level1.start_level()
                            except Exception as e:
                                print(f"Error loading level1 module: {e}")
                                pygame.quit()
                                sys.exit()
                        elif selected_index == 1:  # Options
                            display_options_menu()
                        elif selected_index == 2:  # Exit
                            pygame.quit()
                            sys.exit()

        # Update flash timer
        flash_timer += 1
        if flash_timer >= flash_interval:
            current_shade = (current_shade + 1) % len(blue_shades)
            flash_timer = 0

        # Determine the current color
        text_color = blue_shades[current_shade]

        # Draw the flashing gradient background
        screen.blit(splash_image, (0, 0))

        # Render menu options with gradient flashing blue shades
        for i, option in enumerate(menu_options):
            if i == selected_index:
                color = text_color  # Flashing blue shades
                outline_color = (0, 0, 0)  # Black outline
                scale_factor = 1.2  # Slightly larger for emphasis
            else:
                color = (255, 255, 255)  # White
                outline_color = (0, 0, 0)  # Black outline
                scale_factor = 1.0  # Normal size

            # Render the text with outline
            text_surface, outline_surface = render_text_with_outline(option, menu_font, color, outline_color, scale_factor)

            # Positioning
            text_rect = text_surface.get_rect(center=(window_size[0] // 2, window_size[1] * 0.65 + i * 60))

            # Draw outline by blitting the outline_surface multiple times with slight offsets
            for dx in [-2, 0, 2]:
                for dy in [-2, 0, 2]:
                    if dx != 0 or dy != 0:
                        outline_rect = outline_surface.get_rect(center=(text_rect.centerx + dx, text_rect.centery + dy))
                        screen.blit(outline_surface, outline_rect)

            # Blit the main text on top
            screen.blit(text_surface, text_rect)

        # Update the display
        pygame.display.flip()
        clock.tick(FPS)

# Function to display the options menu
def display_options_menu():
    selected_index = 0
    options = ["Toggle Fullscreen", "Toggle Music", "Controls", "Back"]
    running = True
    flash_timer = 0
    flash_interval = 30  # Frames between color toggles
    blue_shades = [
        (0, 191, 255),
        (30, 144, 255),
        (100, 149, 237),
        (70, 130, 180)
    ]
    current_shade = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    selected_index = (selected_index - 1) % len(options)
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    selected_index = (selected_index + 1) % len(options)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if selected_index == 0:  # Toggle Fullscreen
                        toggle_setting('fullscreen')
                    elif selected_index == 1:  # Toggle Music
                        toggle_setting('music_on')
                    elif selected_index == 2:  # Controls
                        display_controls_menu()
                    elif selected_index == 3:  # Back
                        running = False
                elif event.key == pygame.K_ESCAPE:
                    running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                # Define clickable regions for each option
                for i, option in enumerate(options):
                    option_rect = pygame.Rect(
                        window_size[0] // 2 - 200, window_size[1] * 0.65 + i * 60 - 25,
                        400, 50
                    )
                    if option_rect.collidepoint(mouse_x, mouse_y):
                        selected_index = i
                        if selected_index == 0:  # Toggle Fullscreen
                            toggle_setting('fullscreen')
                        elif selected_index == 1:  # Toggle Music
                            toggle_setting('music_on')
                        elif selected_index == 2:  # Controls
                            display_controls_menu()
                        elif selected_index == 3:  # Back
                            running = False

        # Update flash timer
        flash_timer += 1
        if flash_timer >= flash_interval:
            current_shade = (current_shade + 1) % len(blue_shades)
            flash_timer = 0

        # Determine the current color
        text_color = blue_shades[current_shade]

        # Draw the flashing gradient background
        screen.blit(splash_image, (0, 0))

        # Render options menu with gradient flashing blue shades
        for i, option in enumerate(options):
            if i == selected_index:
                color = text_color  # Flashing blue shades
                outline_color = (0, 0, 0)  # Black outline
                scale_factor = 1.2  # Slightly larger for emphasis
            else:
                color = (255, 255, 255)  # White
                outline_color = (0, 0, 0)  # Black outline
                scale_factor = 1.0  # Normal size

            # Render the text with outline
            text_surface, outline_surface = render_text_with_outline(option, menu_font, color, outline_color, scale_factor)

            # Positioning
            text_rect = text_surface.get_rect(center=(window_size[0] // 2, window_size[1] * 0.65 + i * 60))

            # Draw outline by blitting the outline_surface multiple times with slight offsets
            for dx in [-2, 0, 2]:
                for dy in [-2, 0, 2]:
                    if dx != 0 or dy != 0:
                        outline_rect = outline_surface.get_rect(center=(text_rect.centerx + dx, text_rect.centery + dy))
                        screen.blit(outline_surface, outline_rect)

            # Blit the main text on top
            screen.blit(text_surface, text_rect)

        # Update the display
        pygame.display.flip()
        clock.tick(FPS)

# Function to display controls menu
def display_controls_menu():
    selected_index = 0
    controls_menu_options = ["View Controls", "Change Controls", "Set Buttons", "Back"]
    running = True
    flash_timer = 0
    flash_interval = 30  # Frames between color toggles
    blue_shades = [
        (34, 139, 34),
        (50, 205, 50),
        (0, 128, 0),
        (0, 100, 0)
    ]
    current_shade = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    selected_index = (selected_index - 1) % len(controls_menu_options)
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    selected_index = (selected_index + 1) % len(controls_menu_options)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if selected_index == 0:  # View Controls
                        view_controls()
                    elif selected_index == 1:  # Change Controls
                        display_change_controls_menu()
                    elif selected_index == 2:  # Set Buttons (not functional)
                        print("Set Buttons selected")  # Placeholder
                    elif selected_index == 3:  # Back
                        running = False
                elif event.key == pygame.K_ESCAPE:
                    running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                # Define clickable regions for each option
                for i, option in enumerate(controls_menu_options):
                    option_rect = pygame.Rect(
                        window_size[0] // 2 - 200, window_size[1] * 0.65 + i * 60 - 25,
                        400, 50
                    )
                    if option_rect.collidepoint(mouse_x, mouse_y):
                        selected_index = i
                        if selected_index == 0:  # View Controls
                            view_controls()
                        elif selected_index == 1:  # Change Controls
                            display_change_controls_menu()
                        elif selected_index == 2:  # Set Buttons
                            print("Set Buttons selected")  # Placeholder
                        elif selected_index == 3:  # Back
                            running = False

        # Update flash timer
        flash_timer += 1
        if flash_timer >= flash_interval:
            current_shade = (current_shade + 1) % len(blue_shades)
            flash_timer = 0

        # Determine the current color
        text_color = blue_shades[current_shade]

        # Draw the flashing gradient background
        screen.blit(splash_image, (0, 0))

        # Render controls menu options with gradient flashing blue shades
        for i, option in enumerate(controls_menu_options):
            if i == selected_index:
                color = text_color  # Flashing blue shades
                outline_color = (0, 0, 0)  # Black outline
                scale_factor = 1.2  # Slightly larger for emphasis
            else:
                color = (255, 255, 255)  # White
                outline_color = (0, 0, 0)  # Black outline
                scale_factor = 1.0  # Normal size

            # Render the text with outline
            text_surface, outline_surface = render_text_with_outline(option, menu_font, color, outline_color, scale_factor)

            # Positioning
            text_rect = text_surface.get_rect(center=(window_size[0] // 2, window_size[1] * 0.65 + i * 60))

            # Draw outline by blitting the outline_surface multiple times with slight offsets
            for dx in [-2, 0, 2]:
                for dy in [-2, 0, 2]:
                    if dx != 0 or dy != 0:
                        outline_rect = outline_surface.get_rect(center=(text_rect.centerx + dx, text_rect.centery + dy))
                        screen.blit(outline_surface, outline_rect)

            # Blit the main text on top
            screen.blit(text_surface, text_rect)

        # Update the display
        pygame.display.flip()
        clock.tick(FPS)

# Function to view controls
def view_controls():
    running = True
    flash_timer = 0
    flash_interval = 30  # Frames between color toggles
    blue_shades = [
        (70, 130, 180),
        (100, 149, 237),
        (30, 144, 255),
        (0, 0, 255)
    ]
    current_shade = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # Update flash timer
        flash_timer += 1
        if flash_timer >= flash_interval:
            current_shade = (current_shade + 1) % len(blue_shades)
            flash_timer = 0

        # Determine the current frame color
        frame_color = blue_shades[current_shade]

        # Draw the flashing gradient background
        screen.blit(splash_image, (0, 0))

        # Define the dimensions for the content area
        box_width = 600
        box_height = 240
        box_x = (window_size[0] - box_width) // 2
        box_y = window_size[1] // 2 - box_height // 2

        # Draw solid black background for the box
        pygame.draw.rect(screen, (0, 0, 0), (box_x, box_y, box_width, box_height))

        # Draw the frame around the box with flashing effect
        pygame.draw.rect(screen, frame_color, (box_x, box_y, box_width, box_height), 5)

        # Draw the title with beautiful font
        title_color = (255, 255, 255)  # White color for the title
        title_surface = menu_font.render("KEY BINDINGS", True, title_color)
        title_rect = title_surface.get_rect(center=(window_size[0] // 2, box_y + 30))
        screen.blit(title_surface, title_rect)

        # Define control texts and their corresponding keys from config
        control_texts = [
            (MOVE_UP, "Move Up", None),
            (MOVE_DOWN, "Move Down", None),
            (SELECT_LEFT_AMMO, "Select Left Ammo", None),
            (SELECT_RIGHT_AMMO, "Select Right Ammo", None),
            (THROW_CARROT, "Throw Carrot", fruit_sprites["carrot"]),
            (THROW_BERRY, "Throw Berry", fruit_sprites["berry"]),
            (THROW_HONEY, "Throw Honey", fruit_sprites["honey"]),
            (THROW_SELECTED_AMMO, "Throw Selected Ammo", None)
        ]

        # Calculate spacing for controls
        left_start_x = box_x + 40
        right_start_x = box_x + 300  # Align with left column
        start_y = box_y + 70  # Starting vertical position for control texts

        # Offset for action text alignment
        action_y_offset = 15  # Offset for text to align closely with buttons

        # Render control texts in two columns
        for i, (key, action, sprite) in enumerate(control_texts):
            if i < 4:  # First four in the left column
                key_rect = pygame.Rect(left_start_x, start_y + (i * 30), 40, 40)  # Adjusted vertical spacing
                action_y = start_y + (i * 30) + action_y_offset  # Adjusted for vertical alignment
            else:  # Last four in the right column
                key_rect = pygame.Rect(right_start_x, start_y + ((i - 4) * 30), 40, 40)  # Adjusted vertical spacing
                action_y = start_y + ((i - 4) * 30) + action_y_offset  # Same offset as left

            # Draw square button rectangle
            pygame.draw.rect(screen, (255, 255, 255), key_rect, 3)  # White outline for button
            pygame.draw.rect(screen, (50, 50, 50), key_rect.inflate(-6, -6))  # Dark grey solid fill

            # Adjust key text size to fit within the button
            fitting_font = get_fitting_font(key, 'freesansbold', key_rect.width, key_rect.height, initial_size=16, min_size=12)
            key_surface = fitting_font.render(key, True, (255, 255, 255))  # White text

            # Center the key text inside the button
            key_text_rect = key_surface.get_rect(center=key_rect.center)
            screen.blit(key_surface, key_text_rect)

            # Draw action text in white color next to the button
            action_color = (255, 255, 255)  # White color for actions
            action_surface = controls_font.render(action, True, action_color)
            if i < 4:
                action_rect = action_surface.get_rect(left=box_x + 100, centery=action_y)  # Close to left column box
            else:
                action_rect = action_surface.get_rect(left=box_x + 360, centery=action_y)  # Close to right column box

            screen.blit(action_surface, action_rect)

            # Draw the fruit sprite next to the action text if available
            if sprite:
                sprite_rect = sprite.get_rect(topleft=(action_rect.right + 10, action_rect.centery - sprite.get_height() // 2))
                screen.blit(sprite, sprite_rect)

        # Update the display
        pygame.display.flip()
        clock.tick(FPS)

# Function to change keybindings menu
def display_change_controls_menu():
    actions = [
        'move_up',
        'move_down',
        'select_left_ammo',
        'select_right_ammo',
        'throw_carrot',
        'throw_berry',
        'throw_honey',
        'throw_selected_ammo'
    ]
    selected_action_index = 0
    running = True
    awaiting_key = False  # Flag to indicate waiting for key input
    flash_timer = 0
    flash_interval = 30  # Frames between color toggles
    blue_shades = [
        (0, 0, 255),
        (30, 144, 255),
        (100, 149, 237),
        (70, 130, 180)
    ]
    current_shade = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if awaiting_key:
                if event.type == pygame.KEYDOWN:
                    new_key = pygame.key.name(event.key).upper()
                    action = actions[selected_action_index]
                    if update_keybinding(action, new_key):
                        print(f"Keybinding for '{action.replace('_', ' ').title()}' updated to '{new_key}'")
                    else:
                        print(f"Failed to update keybinding for '{action.replace('_', ' ').title()}'")
                    awaiting_key = False
            else:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        selected_action_index = (selected_action_index - 1) % len(actions)
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        selected_action_index = (selected_action_index + 1) % len(actions)
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        awaiting_key = True
                    elif event.key == pygame.K_ESCAPE:
                        running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = event.pos
                    for i, action in enumerate(actions):
                        option_rect = pygame.Rect(
                            window_size[0] // 2 - 200, window_size[1] * 0.35 + i * 40 - 12,
                            400, 24
                        )
                        if option_rect.collidepoint(mouse_x, mouse_y):
                            selected_action_index = i
                            awaiting_key = True
                    # Check if "Reset to Defaults" button is clicked
                    reset_box_width = 200
                    reset_box_height = 50
                    reset_box_x = window_size[0] // 2 - reset_box_width // 2
                    reset_box_y = window_size[1] // 2 + 200  # Positioned below the keybindings
                    reset_rect = pygame.Rect(reset_box_x, reset_box_y, reset_box_width, reset_box_height)
                    if reset_rect.collidepoint(mouse_x, mouse_y):
                        reset_to_defaults()

        # Update flash timer
        flash_timer += 1
        if flash_timer >= flash_interval:
            current_shade = (current_shade + 1) % len(blue_shades)
            flash_timer = 0

        # Determine the current color
        if selected_action_index < len(actions):
            if awaiting_key:
                color = (255, 0, 0)  # Red color when awaiting key input
            else:
                color = blue_shades[current_shade]
        else:
            color = (255, 255, 255)  # Default to white

        # Draw the flashing gradient background
        screen.blit(splash_image, (0, 0))

        # Render keybindings menu with gradient flashing blue shades
        for i, action in enumerate(actions):
            if i == selected_action_index and awaiting_key:
                display_text = f"Press new key for {action.replace('_', ' ').title()}:"
                current_color = (255, 0, 0)  # Red color when awaiting key input
                outline_color = (0, 0, 0)  # Black outline
                scale_factor = 1.2  # Slightly larger
            elif i == selected_action_index:
                display_text = f"{action.replace('_', ' ').title()}: {config.get('KeyBindings', action)}"
                current_color = color  # Flashing blue shades
                outline_color = (0, 0, 0)  # Black outline
                scale_factor = 1.2
            else:
                display_text = f"{action.replace('_', ' ').title()}: {config.get('KeyBindings', action)}"
                current_color = (255, 255, 255)  # White color
                outline_color = (0, 0, 0)  # Black outline
                scale_factor = 1.0

            # Render the text with outline
            text_surface, outline_surface = render_text_with_outline(display_text, controls_font, current_color, outline_color, scale_factor)

            # Positioning
            text_rect = text_surface.get_rect(center=(window_size[0] // 2, window_size[1] * 0.35 + i * 40))

            # Draw outline by blitting the outline_surface multiple times with slight offsets
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx != 0 or dy != 0:
                        outline_rect = outline_surface.get_rect(center=(text_rect.centerx + dx, text_rect.centery + dy))
                        screen.blit(outline_surface, outline_rect)

            # Blit the main text on top
            screen.blit(text_surface, text_rect)

        # Draw the black box for "Reset to Defaults" button
        reset_box_width = 200
        reset_box_height = 50
        reset_box_x = window_size[0] // 2 - reset_box_width // 2
        reset_box_y = window_size[1] // 2 + 200  # Positioned below the keybindings

        pygame.draw.rect(screen, (0, 0, 0), (reset_box_x, reset_box_y, reset_box_width, reset_box_height))
        pygame.draw.rect(screen, (255, 255, 255), (reset_box_x, reset_box_y, reset_box_width, reset_box_height), 2)

        # Render the "Reset to Defaults" button text
        reset_text = "Reset to Defaults"
        reset_text_color = (255, 255, 255)  # White color
        reset_text_surface = controls_font.render(reset_text, True, reset_text_color)
        reset_text_rect = reset_text_surface.get_rect(center=(reset_box_x + reset_box_width // 2, reset_box_y + reset_box_height // 2))
        screen.blit(reset_text_surface, reset_text_rect)

        # Update the display
        pygame.display.flip()
        clock.tick(FPS)

# Function to view controls
def view_controls():
    running = True
    flash_timer = 0
    flash_interval = 30  # Frames between color toggles
    blue_shades = [
        (70, 130, 180),
        (100, 149, 237),
        (30, 144, 255),
        (0, 0, 255)
    ]
    current_shade = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # Update flash timer
        flash_timer += 1
        if flash_timer >= flash_interval:
            current_shade = (current_shade + 1) % len(blue_shades)
            flash_timer = 0

        # Determine the current frame color
        frame_color = blue_shades[current_shade]

        # Draw the flashing gradient background
        screen.blit(splash_image, (0, 0))

        # Define the dimensions for the content area
        box_width = 600
        box_height = 240
        box_x = (window_size[0] - box_width) // 2
        box_y = window_size[1] // 2 - box_height // 2

        # Draw solid black background for the box
        pygame.draw.rect(screen, (0, 0, 0), (box_x, box_y, box_width, box_height))

        # Draw the frame around the box with flashing effect
        pygame.draw.rect(screen, frame_color, (box_x, box_y, box_width, box_height), 5)

        # Draw the title with beautiful font
        title_color = (255, 255, 255)  # White color for the title
        title_surface = menu_font.render("KEY BINDINGS", True, title_color)
        title_rect = title_surface.get_rect(center=(window_size[0] // 2, box_y + 30))
        screen.blit(title_surface, title_rect)

        # Define control texts and their corresponding keys from config
        control_texts = [
            (MOVE_UP, "Move Up", None),
            (MOVE_DOWN, "Move Down", None),
            (SELECT_LEFT_AMMO, "Select Left Ammo", None),
            (SELECT_RIGHT_AMMO, "Select Right Ammo", None),
            (THROW_CARROT, "Throw Carrot", fruit_sprites["carrot"]),
            (THROW_BERRY, "Throw Berry", fruit_sprites["berry"]),
            (THROW_HONEY, "Throw Honey", fruit_sprites["honey"]),
            (THROW_SELECTED_AMMO, "Throw Selected Ammo", None)
        ]

        # Calculate spacing for controls
        left_start_x = box_x + 40
        right_start_x = box_x + 300  # Align with left column
        start_y = box_y + 70  # Starting vertical position for control texts

        # Offset for action text alignment
        action_y_offset = 15  # Offset for text to align closely with buttons

        # Render control texts in two columns
        for i, (key, action, sprite) in enumerate(control_texts):
            if i < 4:  # First four in the left column
                key_rect = pygame.Rect(left_start_x, start_y + (i * 30), 40, 40)  # Adjusted vertical spacing
                action_y = start_y + (i * 30) + action_y_offset  # Adjusted for vertical alignment
            else:  # Last four in the right column
                key_rect = pygame.Rect(right_start_x, start_y + ((i - 4) * 30), 40, 40)  # Adjusted vertical spacing
                action_y = start_y + ((i - 4) * 30) + action_y_offset  # Same offset as left

            # Draw square button rectangle
            pygame.draw.rect(screen, (255, 255, 255), key_rect, 3)  # White outline for button
            pygame.draw.rect(screen, (50, 50, 50), key_rect.inflate(-6, -6))  # Dark grey solid fill

            # Adjust key text size to fit within the button
            fitting_font = get_fitting_font(key, 'freesansbold', key_rect.width, key_rect.height, initial_size=16, min_size=12)
            key_surface = fitting_font.render(key, True, (255, 255, 255))  # White text

            # Center the key text inside the button
            key_text_rect = key_surface.get_rect(center=key_rect.center)
            screen.blit(key_surface, key_text_rect)

            # Draw action text in white color next to the button
            action_color = (255, 255, 255)  # White color for actions
            action_surface = controls_font.render(action, True, action_color)
            if i < 4:
                action_rect = action_surface.get_rect(left=box_x + 100, centery=action_y)  # Close to left column box
            else:
                action_rect = action_surface.get_rect(left=box_x + 360, centery=action_y)  # Close to right column box

            screen.blit(action_surface, action_rect)

            # Draw the fruit sprite next to the action text if available
            if sprite:
                sprite_rect = sprite.get_rect(topleft=(action_rect.right + 10, action_rect.centery - sprite.get_height() // 2))
                screen.blit(sprite, sprite_rect)

        # Update the display
        pygame.display.flip()
        clock.tick(FPS)

# Function to change keybindings menu with dynamic text resizing
def display_change_controls_menu():
    actions = [
        'move_up',
        'move_down',
        'select_left_ammo',
        'select_right_ammo',
        'throw_carrot',
        'throw_berry',
        'throw_honey',
        'throw_selected_ammo'
    ]
    selected_action_index = 0
    running = True
    awaiting_key = False  # Flag to indicate waiting for key input
    flash_timer = 0
    flash_interval = 30  # Frames between color toggles
    blue_shades = [
        (0, 0, 255),
        (30, 144, 255),
        (100, 149, 237),
        (70, 130, 180)
    ]
    current_shade = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if awaiting_key:
                if event.type == pygame.KEYDOWN:
                    new_key = pygame.key.name(event.key).upper()
                    action = actions[selected_action_index]
                    if update_keybinding(action, new_key):
                        print(f"Keybinding for '{action.replace('_', ' ').title()}' updated to '{new_key}'")
                    else:
                        print(f"Failed to update keybinding for '{action.replace('_', ' ').title()}'")
                    awaiting_key = False
            else:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        selected_action_index = (selected_action_index - 1) % len(actions)
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        selected_action_index = (selected_action_index + 1) % len(actions)
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        awaiting_key = True
                    elif event.key == pygame.K_ESCAPE:
                        running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = event.pos
                    for i, action in enumerate(actions):
                        option_rect = pygame.Rect(
                            window_size[0] // 2 - 200, window_size[1] * 0.35 + i * 40 - 12,
                            400, 24
                        )
                        if option_rect.collidepoint(mouse_x, mouse_y):
                            selected_action_index = i
                            awaiting_key = True
                    # Check if "Reset to Defaults" button is clicked
                    reset_box_width = 200
                    reset_box_height = 50
                    reset_box_x = window_size[0] // 2 - reset_box_width // 2
                    reset_box_y = window_size[1] // 2 + 200  # Positioned below the keybindings
                    reset_rect = pygame.Rect(reset_box_x, reset_box_y, reset_box_width, reset_box_height)
                    if reset_rect.collidepoint(mouse_x, mouse_y):
                        reset_to_defaults()

        # Update flash timer
        flash_timer += 1
        if flash_timer >= flash_interval:
            current_shade = (current_shade + 1) % len(blue_shades)
            flash_timer = 0

        # Determine the current color
        if selected_action_index < len(actions):
            if awaiting_key:
                color = (255, 0, 0)  # Red color when awaiting key input
            else:
                color = blue_shades[current_shade]
        else:
            color = (255, 255, 255)  # Default to white

        # Draw the flashing gradient background
        screen.blit(splash_image, (0, 0))

        # Render keybindings menu with gradient flashing blue shades
        for i, action in enumerate(actions):
            if i == selected_action_index and awaiting_key:
                display_text = f"Press new key for {action.replace('_', ' ').title()}:"
                current_color = (255, 0, 0)  # Red color when awaiting key input
                outline_color = (0, 0, 0)  # Black outline
                scale_factor = 1.2  # Slightly larger
            elif i == selected_action_index:
                display_text = f"{action.replace('_', ' ').title()}: {config.get('KeyBindings', action)}"
                current_color = color  # Flashing blue shades
                outline_color = (0, 0, 0)  # Black outline
                scale_factor = 1.2
            else:
                display_text = f"{action.replace('_', ' ').title()}: {config.get('KeyBindings', action)}"
                current_color = (255, 255, 255)  # White color
                outline_color = (0, 0, 0)  # Black outline
                scale_factor = 1.0

            # Render the text with outline
            text_surface, outline_surface = render_text_with_outline(display_text, controls_font, current_color, outline_color, scale_factor)

            # Positioning
            text_rect = text_surface.get_rect(center=(window_size[0] // 2, window_size[1] * 0.35 + i * 40))

            # Draw outline by blitting the outline_surface multiple times with slight offsets
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx != 0 or dy != 0:
                        outline_rect = outline_surface.get_rect(center=(text_rect.centerx + dx, text_rect.centery + dy))
                        screen.blit(outline_surface, outline_rect)

            # Blit the main text on top
            screen.blit(text_surface, text_rect)

        # Draw the black box for "Reset to Defaults" button
        reset_box_width = 200
        reset_box_height = 50
        reset_box_x = window_size[0] // 2 - reset_box_width // 2
        reset_box_y = window_size[1] // 2 + 200  # Positioned below the keybindings

        pygame.draw.rect(screen, (0, 0, 0), (reset_box_x, reset_box_y, reset_box_width, reset_box_height))
        pygame.draw.rect(screen, (255, 255, 255), (reset_box_x, reset_box_y, reset_box_width, reset_box_height), 2)

        # Render the "Reset to Defaults" button text
        reset_text = "Reset to Defaults"
        reset_text_color = (255, 255, 255)  # White color
        reset_text_surface = controls_font.render(reset_text, True, reset_text_color)
        reset_text_rect = reset_text_surface.get_rect(center=(reset_box_x + reset_box_width // 2, reset_box_y + reset_box_height // 2))
        screen.blit(reset_text_surface, reset_text_rect)

        # Update the display
        pygame.display.flip()
        clock.tick(FPS)

# Function to view controls
def view_controls():
    running = True
    flash_timer = 0
    flash_interval = 30  # Frames between color toggles
    blue_shades = [
        (70, 130, 180),
        (100, 149, 237),
        (30, 144, 255),
        (0, 0, 255)
    ]
    current_shade = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # Update flash timer
        flash_timer += 1
        if flash_timer >= flash_interval:
            current_shade = (current_shade + 1) % len(blue_shades)
            flash_timer = 0

        # Determine the current frame color
        frame_color = blue_shades[current_shade]

        # Draw the flashing gradient background
        screen.blit(splash_image, (0, 0))

        # Define the dimensions for the content area
        box_width = 600
        box_height = 240
        box_x = (window_size[0] - box_width) // 2
        box_y = window_size[1] // 2 - box_height // 2

        # Draw solid black background for the box
        pygame.draw.rect(screen, (0, 0, 0), (box_x, box_y, box_width, box_height))

        # Draw the frame around the box with flashing effect
        pygame.draw.rect(screen, frame_color, (box_x, box_y, box_width, box_height), 5)

        # Draw the title with beautiful font
        title_color = (255, 255, 255)  # White color for the title
        title_surface = menu_font.render("KEY BINDINGS", True, title_color)
        title_rect = title_surface.get_rect(center=(window_size[0] // 2, box_y + 30))
        screen.blit(title_surface, title_rect)

        # Define control texts and their corresponding keys from config
        control_texts = [
            (MOVE_UP, "Move Up", None),
            (MOVE_DOWN, "Move Down", None),
            (SELECT_LEFT_AMMO, "Select Left Ammo", None),
            (SELECT_RIGHT_AMMO, "Select Right Ammo", None),
            (THROW_CARROT, "Throw Carrot", fruit_sprites["carrot"]),
            (THROW_BERRY, "Throw Berry", fruit_sprites["berry"]),
            (THROW_HONEY, "Throw Honey", fruit_sprites["honey"]),
            (THROW_SELECTED_AMMO, "Throw Selected Ammo", None)
        ]

        # Calculate spacing for controls
        left_start_x = box_x + 40
        right_start_x = box_x + 300  # Align with left column
        start_y = box_y + 70  # Starting vertical position for control texts

        # Offset for action text alignment
        action_y_offset = 15  # Offset for text to align closely with buttons

        # Render control texts in two columns
        for i, (key, action, sprite) in enumerate(control_texts):
            if i < 4:  # First four in the left column
                key_rect = pygame.Rect(left_start_x, start_y + (i * 30), 40, 40)  # Adjusted vertical spacing
                action_y = start_y + (i * 30) + action_y_offset  # Adjusted for vertical alignment
            else:  # Last four in the right column
                key_rect = pygame.Rect(right_start_x, start_y + ((i - 4) * 30), 40, 40)  # Adjusted vertical spacing
                action_y = start_y + ((i - 4) * 30) + action_y_offset  # Same offset as left

            # Draw square button rectangle
            pygame.draw.rect(screen, (255, 255, 255), key_rect, 3)  # White outline for button
            pygame.draw.rect(screen, (50, 50, 50), key_rect.inflate(-6, -6))  # Dark grey solid fill

            # Adjust key text size to fit within the button
            fitting_font = get_fitting_font(key, 'freesansbold', key_rect.width, key_rect.height, initial_size=16, min_size=12)
            key_surface = fitting_font.render(key, True, (255, 255, 255))  # White text

            # Center the key text inside the button
            key_text_rect = key_surface.get_rect(center=key_rect.center)
            screen.blit(key_surface, key_text_rect)

            # Draw action text in white color next to the button
            action_color = (255, 255, 255)  # White color for actions
            action_surface = controls_font.render(action, True, action_color)
            if i < 4:
                action_rect = action_surface.get_rect(left=box_x + 100, centery=action_y)  # Close to left column box
            else:
                action_rect = action_surface.get_rect(left=box_x + 360, centery=action_y)  # Close to right column box

            screen.blit(action_surface, action_rect)

            # Draw the fruit sprite next to the action text if available
            if sprite:
                sprite_rect = sprite.get_rect(topleft=(action_rect.right + 10, action_rect.centery - sprite.get_height() // 2))
                screen.blit(sprite, sprite_rect)

        # Update the display
        pygame.display.flip()
        clock.tick(FPS)

# Function to display change controls menu with dynamic text resizing and black box
def display_change_controls_menu():
    actions = [
        'move_up',
        'move_down',
        'select_left_ammo',
        'select_right_ammo',
        'throw_carrot',
        'throw_berry',
        'throw_honey',
        'throw_selected_ammo'
    ]
    selected_action_index = 0
    running = True
    awaiting_key = False  # Flag to indicate waiting for key input
    flash_timer = 0
    flash_interval = 30  # Frames between color toggles
    blue_shades = [
        (0, 0, 255),
        (30, 144, 255),
        (100, 149, 237),
        (70, 130, 180)
    ]
    current_shade = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if awaiting_key:
                if event.type == pygame.KEYDOWN:
                    new_key = pygame.key.name(event.key).upper()
                    action = actions[selected_action_index]
                    if update_keybinding(action, new_key):
                        print(f"Keybinding for '{action.replace('_', ' ').title()}' updated to '{new_key}'")
                    else:
                        print(f"Failed to update keybinding for '{action.replace('_', ' ').title()}'")
                    awaiting_key = False
            else:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        selected_action_index = (selected_action_index - 1) % len(actions)
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        selected_action_index = (selected_action_index + 1) % len(actions)
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        awaiting_key = True
                    elif event.key == pygame.K_ESCAPE:
                        running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = event.pos
                    for i, action in enumerate(actions):
                        option_rect = pygame.Rect(
                            window_size[0] // 2 - 200, window_size[1] * 0.35 + i * 40 - 12,
                            400, 24
                        )
                        if option_rect.collidepoint(mouse_x, mouse_y):
                            selected_action_index = i
                            awaiting_key = True
                    # Check if "Reset to Defaults" button is clicked
                    reset_box_width = 200
                    reset_box_height = 50
                    reset_box_x = window_size[0] // 2 - reset_box_width // 2
                    reset_box_y = window_size[1] // 2 + 200  # Positioned below the keybindings
                    reset_rect = pygame.Rect(reset_box_x, reset_box_y, reset_box_width, reset_box_height)
                    if reset_rect.collidepoint(mouse_x, mouse_y):
                        reset_to_defaults()

        # Update flash timer
        flash_timer += 1
        if flash_timer >= flash_interval:
            current_shade = (current_shade + 1) % len(blue_shades)
            flash_timer = 0

        # Determine the current color
        if selected_action_index < len(actions):
            if awaiting_key:
                color = (255, 0, 0)  # Red color when awaiting key input
            else:
                color = blue_shades[current_shade]
        else:
            color = (255, 255, 255)  # Default to white

        # Draw the flashing gradient background
        screen.blit(splash_image, (0, 0))

        # Render keybindings menu with gradient flashing blue shades
        for i, action in enumerate(actions):
            if i == selected_action_index and awaiting_key:
                display_text = f"Press new key for {action.replace('_', ' ').title()}:"
                current_color = (255, 0, 0)  # Red color when awaiting key input
                outline_color = (0, 0, 0)  # Black outline
                scale_factor = 1.2  # Slightly larger
            elif i == selected_action_index:
                display_text = f"{action.replace('_', ' ').title()}: {config.get('KeyBindings', action)}"
                current_color = color  # Flashing blue shades
                outline_color = (0, 0, 0)  # Black outline
                scale_factor = 1.2
            else:
                display_text = f"{action.replace('_', ' ').title()}: {config.get('KeyBindings', action)}"
                current_color = (255, 255, 255)  # White color
                outline_color = (0, 0, 0)  # Black outline
                scale_factor = 1.0

            # Render the text with outline
            text_surface, outline_surface = render_text_with_outline(display_text, controls_font, current_color, outline_color, scale_factor)

            # Positioning
            text_rect = text_surface.get_rect(center=(window_size[0] // 2, window_size[1] * 0.35 + i * 40))

            # Draw outline by blitting the outline_surface multiple times with slight offsets
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx != 0 or dy != 0:
                        outline_rect = outline_surface.get_rect(center=(text_rect.centerx + dx, text_rect.centery + dy))
                        screen.blit(outline_surface, outline_rect)

            # Blit the main text on top
            screen.blit(text_surface, text_rect)

        # Draw the black box for "Reset to Defaults" button
        reset_box_width = 200
        reset_box_height = 50
        reset_box_x = window_size[0] // 2 - reset_box_width // 2
        reset_box_y = window_size[1] // 2 + 200  # Positioned below the keybindings

        # Draw black box behind the button
        pygame.draw.rect(screen, (0, 0, 0), (reset_box_x, reset_box_y, reset_box_width, reset_box_height))
        pygame.draw.rect(screen, (255, 255, 255), (reset_box_x, reset_box_y, reset_box_width, reset_box_height), 2)

        # Render the "Reset to Defaults" button text
        reset_text = "Reset to Defaults"
        reset_text_color = (255, 255, 255)  # White color
        reset_text_surface = controls_font.render(reset_text, True, reset_text_color)
        reset_text_rect = reset_text_surface.get_rect(center=(reset_box_x + reset_box_width // 2, reset_box_y + reset_box_height // 2))
        screen.blit(reset_text_surface, reset_text_rect)

        # Update the display
        pygame.display.flip()
        clock.tick(FPS)

# ---------------------------- #
#          Main Loop           #
# ---------------------------- #

if __name__ == "__main__":
    display_start_menu()
    pygame.quit()
    sys.exit()
