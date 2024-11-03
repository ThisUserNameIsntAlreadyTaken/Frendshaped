import pygame
import random

# Snow class for level 3
class Snow:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = random.randint(10, 20)  # Random size for the snowflake shapes
        self.speed_y = random.uniform(1, 2)  # Falling speed
        self.sway_direction = random.choice([-1, 1])  # Random sway direction
        self.sway_amount = 0
        self.wind_resistance = random.uniform(0.5, 1.0)  # Each snowflake has its own resistance to wind

    def update(self, wind_is_blowing, wind_speed):
        if wind_is_blowing:
            # Apply wind speed, factoring in the snowflake's wind resistance
            self.x += wind_speed * self.wind_resistance
        else:
            # Swaying logic: sway by 15 pixels to each side
            self.sway_amount += self.sway_direction
            if abs(self.sway_amount) > 15:
                self.sway_direction *= -1  # Change direction at sway limit
            self.x += self.sway_direction
        self.y += self.speed_y  # Continue falling

    def draw(self, screen):
        # Draw the white snowflake shape (just a circle for now)
        pygame.draw.circle(screen, (255, 255, 255), (self.x, self.y), self.size // 2)

# Function to create snowflakes
def create_snow(root_dir, count=1):
    return [Snow(random.randint(0, 800), random.randint(-100, 0)) for _ in range(count)]

# Function to update and draw snowflakes
def update_and_draw_snow(screen, snowflakes, root_dir, spawn_timer, wind_is_blowing, wind_speed, wind_spawn_timer):
    # Update and draw snowflakes
    for snow in snowflakes[:]:
        snow.update(wind_is_blowing, wind_speed)
        snow.draw(screen)
        if snow.y > 600:  # Remove snowflakes that fall off the bottom of the screen
            snowflakes.remove(snow)

    # Check whether to spawn new snowflakes (randomly between 10 and 30 every 2 seconds)
    if spawn_timer[0] <= 0:
        snow_to_spawn = random.randint(10, 30)
        for _ in range(snow_to_spawn):
            new_snow = Snow(random.randint(0, 800), random.randint(-100, 0))
            snowflakes.append(new_snow)
        spawn_timer[0] = 120  # 2 seconds at 60 FPS

    # Wind-based snow: spawn 10 snowflakes per second on the left when wind is blowing
    if wind_is_blowing and wind_spawn_timer[0] <= 0:
        for _ in range(10):
            new_snow = Snow(-20, random.randint(0, 600))  # Spawn just outside the left
            snowflakes.append(new_snow)
        wind_spawn_timer[0] = 6  # Set wind spawn timer to allow 10 snowflakes per second (60 FPS / 6)

    # Decrease spawn timers
    spawn_timer[0] -= 1
    wind_spawn_timer[0] -= 1

# Wind simulator function (same as autumn)
def wind_simulator(wind_timer, wind_duration, wind_speed):
    if wind_timer[0] <= 0:
        wind_duration[0] = random.randint(360, 600)  # Wind blows for 6 to 10 seconds
        wind_timer[0] = random.randint(600, 900)  # Wind starts again in 10 to 15 seconds
        wind_speed[0] = random.uniform(0.5, 1)  # Wind starts slow
        return True
    elif wind_duration[0] > 0:
        if wind_speed[0] < 5 * wind_speed[1]:
            wind_speed[0] += random.uniform(0.05, 0.2)  # Wind speeds up
        wind_duration[0] -= 1
        return True
    else:
        if wind_speed[0] > wind_speed[1]:
            wind_speed[0] -= wind_speed[0] * 0.05  # Gradual wind slowdown
        else:
            wind_speed[0] = wind_speed[1]
            wind_timer[0] -= 1  # No wind, count down until next event
        return False
