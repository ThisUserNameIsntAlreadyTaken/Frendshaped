import pygame
import random

# Leaf class for level 2
class Leaf:
    def __init__(self, x, y, image):
        self.x = x
        self.y = y
        self.original_image = pygame.transform.scale(image, (20, 20))  # Original image (20x20)
        self.image = self.original_image  # This will be updated as the image rotates
        self.speed_y = random.uniform(1, 2)  # Falling speed
        self.sway_direction = random.choice([-1, 1])  # Random sway direction
        self.sway_amount = 0
        self.rotation_angle = 0  # Initialize rotation angle

    def update(self, wind_is_blowing, wind_speed):
        if wind_is_blowing:
            self.x += wind_speed  # Apply wind speed if wind is blowing
            self.y += self.speed_y  # Continue falling
        else:
            # Swaying logic: sway by 15 pixels to each side
            self.sway_amount += self.sway_direction
            if abs(self.sway_amount) > 15:
                self.sway_direction *= -1  # Change direction at sway limit
            self.x += self.sway_direction
            self.y += self.speed_y  # Continue falling

            # Rotate the leaf by incrementing the angle
            self.rotation_angle += 5  # Rotate by 5 degrees per frame
            if self.rotation_angle >= 360:
                self.rotation_angle = 0  # Reset angle after a full spin
            # Rotate the image using the rotation angle
            self.image = pygame.transform.rotate(self.original_image, self.rotation_angle)

    def draw(self, screen):
        # Draw the rotated image at the leaf's position
        rotated_rect = self.image.get_rect(center=(self.x, self.y))
        screen.blit(self.image, rotated_rect.topleft)

# Function to load leaf images
def create_leaf_images(root_dir):
    # Load leaf images
    leaf_images = [pygame.image.load(f"{root_dir}/art/leaf{i}.png").convert_alpha() for i in range(1, 3)]
    return leaf_images  # Return the list of leaf surfaces

# Function to create leaves
def create_leaves(root_dir, count=1):
    leaf_images = create_leaf_images(root_dir)
    # Create and return individual leaf instances
    return [Leaf(random.randint(0, 800), random.randint(-100, 0), random.choice(leaf_images)) for _ in range(count)]

# Function to update and draw leaves
def update_and_draw_leaves(screen, leaves, root_dir, spawn_timer, wind_is_blowing, wind_speed, wind_spawn_timer):
    # Update and draw leaves
    for leaf in leaves[:]:
        leaf.update(wind_is_blowing, wind_speed)
        leaf.draw(screen)
        if leaf.y > 600:  # Remove leaves that fall off the bottom of the screen
            leaves.remove(leaf)

    # Check whether to spawn a new leaf (randomly between 10 and 30 every 2 seconds)
    if spawn_timer[0] <= 0:
        leaf_images = create_leaf_images(root_dir)
        # Randomly determine how many leaves to spawn (between 10 and 30)
        leaves_to_spawn = random.randint(10, 30)
        for _ in range(leaves_to_spawn):
            new_leaf = Leaf(random.randint(0, 800), random.randint(-100, 0), random.choice(leaf_images))
            leaves.append(new_leaf)
        spawn_timer[0] = 120  # 2 seconds at 60 FPS

    # Wind-based leaves: spawn 10 leaves per second on the left when wind is blowing
    if wind_is_blowing and wind_spawn_timer[0] <= 0:
        leaf_images = create_leaf_images(root_dir)
        # Spawn 10 individual leaves per second
        for _ in range(10):
            new_leaf = Leaf(-20, random.randint(0, 600), random.choice(leaf_images))  # Spawn just outside the left
            leaves.append(new_leaf)
        wind_spawn_timer[0] = 6  # Set wind spawn timer to allow 10 leaves per second (60 FPS / 6)

    # Decrease spawn timers
    spawn_timer[0] -= 1
    wind_spawn_timer[0] -= 1

# Wind simulator function with gradual slowdown
def wind_simulator(wind_timer, wind_duration, wind_speed):
    # Wind blows randomly every 10 to 15 seconds for 6 to 10 seconds
    if wind_timer[0] <= 0:
        wind_duration[0] = random.randint(360, 600)  # Wind blows for 6 to 10 seconds
        wind_timer[0] = random.randint(600, 900)  # Wind starts again in 10 to 15 seconds
        wind_speed[0] = random.uniform(0.5, 1)  # Wind starts slow
        return True
    elif wind_duration[0] > 0:
        # Gradually increase wind speed to up to 5x the base speed
        if wind_speed[0] < 5 * wind_speed[1]:
            wind_speed[0] += random.uniform(0.05, 0.2)  # Wind speeds up at random intervals
        wind_duration[0] -= 1  # Wind is still blowing
        return True
    else:
        # Gradually decrease the wind speed more smoothly
        if wind_speed[0] > wind_speed[1]:
            # Slow down more gradually: the decrease slows as wind_speed approaches the base speed
            wind_speed[0] -= wind_speed[0] * 0.05  # Decrease wind speed by 5% of current speed
        else:
            wind_speed[0] = wind_speed[1]  # Ensure it doesn't go below base speed
            wind_timer[0] -= 1  # No wind, count down until the next wind event
        return False
