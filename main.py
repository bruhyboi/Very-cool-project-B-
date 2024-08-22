from neopixel import NeoPixel
import machine as m
from machine import Timer
from time import sleep_ms as s
import random
from machine import Pin
from rotary_irq_rp2 import RotaryIRQ
import time

button = Pin(16, Pin.IN, Pin.PULL_UP)
encoder = RotaryIRQ(15, 14, min_val=0, max_val=255, incr=1, range_mode=RotaryIRQ.RANGE_BOUNDED, pull_up=True)
current_val = 0
"""
MODES:
Mode 0 = Brightness
Mode 1 = Red
Mode 2 = Green
Mode 3 = Blue
Mode 4 = Anims
"""

# MODE 4 ANIMS : rainbow() | snake() | fade()

mode = 0
np = NeoPixel(m.Pin(0), 8 * 32)

MAX_BRIGHTNESS = 25
BRIGHTNESS_SCALE = MAX_BRIGHTNESS / 255

def mode_change(x):
    if x == 4:
        x = 0
    else:
        x += 1
    return x

def wheel(pos):
    pos = pos % 255
    if pos < 85:
        r = pos * 3
        g = 255 - pos * 3
        b = 0
    elif pos < 170:
        pos -= 85
        r = 255 - pos * 3
        g = 0
        b = pos * 3
    else:
        pos -= 170
        r = 0
        g = pos * 3
        b = 255 - pos * 3
    
    r = int(r * BRIGHTNESS_SCALE)
    g = int(g * BRIGHTNESS_SCALE)
    b = int(b * BRIGHTNESS_SCALE)
    
    return (r, g, b)

rainbow_offset = 0

def rainbow():
    global rainbow_offset
    num_pixels = np.n
    for i in range(num_pixels):
        np[i] = wheel((i + rainbow_offset) % 255)
    np.write()
    rainbow_offset = (rainbow_offset + 5) % 255

def rand():
    r = random.randrange(0, 255, 1)
    g = random.randrange(0, 255, 1)
    b = random.randrange(0, 255, 1)

    r = int(r * BRIGHTNESS_SCALE)
    g = int(g * BRIGHTNESS_SCALE)
    b = int(b * BRIGHTNESS_SCALE)

    return (r, g, b)

def sarpe(x, a):
    # Ensures x + i is within bounds
    for i in range(32):
        if 0 <= x + i < 256:  # Ensure we're within matrix bounds
            np[x + i] = a

def sarpe2(x, a):
    # Ensures x - i is within bounds
    for i in range(32):
        if 0 <= x - i < 256:  # Ensure we're within matrix bounds
            np[x - i] = a

# State variables for the snake animation
snake_position = 0
snake_direction = 1  # 1 for forward, -1 for backward
snake_tick_speed = 2
snake_step = 0

def snake():
    global snake_position, snake_direction, snake_tick_speed, snake_step

    # Determine color
    a = rand()

    # Forward snake movement
    if snake_direction == 1:
        for x in range(0, 224, snake_tick_speed):
            sarpe(x, a)
            np.write()
            s(1)
            np[x] = (0, 0, 0)
            s(2)
            np.write()
            
    # Backward snake movement
    else:
        for x in range(255, 30, -snake_tick_speed):
            sarpe2(x, a)
            np.write()
            s(1)
            np[x] = (0, 0, 0)
            s(2)
            np.write()


    snake_direction *= -1
    snake_tick_speed += 1
    if snake_tick_speed > 8:
        snake_tick_speed = 2

# State variables for the fade animation
fade_value = 0
fade_direction = 1  # 1 for increasing brightness, -1 for decreasing
fade_step = 1  # Adjust this to control the speed of fading

def fade():
    global fade_value, fade_direction

    # Update the LED strip with the current brightness
    np.fill((fade_value, fade_value, fade_value))
    s(40)
    np.write()

    # Update the fade value
    fade_value += fade_direction * fade_step

    # Reverse direction if we reach the limits
    if fade_value >= 25 or fade_value <= 0:
        fade_direction *= -1

# Initialize mode, color values, last encoder value, and animation state
mode = 0
r, g, b = 0, 0, 0
last_encoder_value = 0
animation_mode = 0  # Variable to keep track of the current animation

def update_animation():
    if mode == 4 and animation_mode == 0:
        rainbow()
    elif mode == 4 and animation_mode == 1:
        snake()
    elif mode == 4 and animation_mode == 2:
        fade()

while True:
    if button.value() == 0:
        # Change mode
        mode = mode_change(mode)
        s(250)
        
        if mode == 4:
            # Reset encoder value to 0 when switching to animation mode
            encoder.reset()
        elif mode != 0:
            # Reset encoder value to 0 when not in brightness mode
            encoder.reset()
        else:
            # Use the last encoder value when switching to brightness mode
            encoder_value = last_encoder_value

    # Read encoder value
    encoder_value = encoder.value()

    if mode == 0:
        # Mode 0: Set brightness for all colors
        r = encoder_value
        g = encoder_value
        b = encoder_value
    elif mode == 1:
        # Mode 1: Adjust red component
        r = encoder_value
    elif mode == 2:
        # Mode 2: Adjust green component
        g = encoder_value
    elif mode == 3:
        # Mode 3: Adjust blue component
        b = encoder_value
    elif mode == 4:
        # Mode 4: Handle animations
        animation_count = 3  # Number of animations
        animation_mode = encoder_value % animation_count  # Cycle through animations
        update_animation()
    
    # Store the last encoder value for use when switching to brightness mode
    last_encoder_value = encoder_value

    if mode != 4:
        # Update LED strip with current color values if not in animation mode
        np.fill((r, g, b))
        np.write()

#made by an idiot. Kind of tells ur skill issue