import pygame
import random
import time
from pygame.locals import *

# Constants
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
BIRD_SPEED = 20
GRAVITY = 2.5
GAME_SPEED = 15

GROUND_WIDTH = 2 * SCREEN_WIDTH
GROUND_HEIGHT = 100

PIPE_WIDTH = 80
PIPE_HEIGHT = 500
PIPE_GAP = 150

WING_SOUND_PATH = 'assets/audio/wing.wav'
HIT_SOUND_PATH = 'assets/audio/hit.wav'

pygame.mixer.init()

class Bird(pygame.sprite.Sprite):
    """Class to represent the Bird in the game."""
    def __init__(self):
        super().__init__()

        # Load bird images for animation
        self.images = [
            pygame.image.load('assets/sprites/bluebird-upflap.png').convert_alpha(),
            pygame.image.load('assets/sprites/bluebird-midflap.png').convert_alpha(),
            pygame.image.load('assets/sprites/bluebird-downflap.png').convert_alpha()
        ]

        self.speed = BIRD_SPEED
        self.current_image = 0
        self.image = self.images[self.current_image]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH / 6
        self.rect.y = SCREEN_HEIGHT / 2

    def update(self):
        """Update the bird's position and animation."""
        self.current_image = (self.current_image + 1) % 3
        self.image = self.images[self.current_image]
        self.speed += GRAVITY
        self.rect.y += self.speed

    def bump(self):
        """Make the bird jump."""
        self.speed = -BIRD_SPEED

    def begin(self):
        """Animate the bird during the start screen."""
        self.current_image = (self.current_image + 1) % 3
        self.image = self.images[self.current_image]

class Pipe(pygame.sprite.Sprite):
    """Class to represent a Pipe in the game."""
    def __init__(self, inverted, xpos, ysize):
        super().__init__()

        self.image = pygame.image.load('assets/sprites/pipe-green.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (PIPE_WIDTH, PIPE_HEIGHT))
        self.rect = self.image.get_rect()
        self.rect.x = xpos

        if inverted:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.y = -(self.rect.height - ysize)
        else:
            self.rect.y = SCREEN_HEIGHT - ysize

        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        """Move the pipe to the left."""
        self.rect.x -= GAME_SPEED

class Ground(pygame.sprite.Sprite):
    """Class to represent the Ground in the game."""
    def __init__(self, xpos):
        super().__init__()

        self.image = pygame.image.load('assets/sprites/base.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (GROUND_WIDTH, GROUND_HEIGHT))
        self.rect = self.image.get_rect()
        self.rect.x = xpos
        self.rect.y = SCREEN_HEIGHT - GROUND_HEIGHT
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        """Move the ground to the left."""
        self.rect.x -= GAME_SPEED

def is_off_screen(sprite):
    """Check if a sprite is off the screen."""
    return sprite.rect.x < -sprite.rect.width

def get_random_pipes(xpos):
    """Generate a pair of pipes (one inverted, one normal) at a given x position."""
    size = random.randint(100, 300)
    bottom_pipe = Pipe(False, xpos, size)
    top_pipe = Pipe(True, xpos, SCREEN_HEIGHT - size - PIPE_GAP)
    return bottom_pipe, top_pipe

# Initialize Pygame and set up the screen
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Flappy Bird')

# Load assets
BACKGROUND = pygame.image.load('assets/sprites/background-day.png')
BACKGROUND = pygame.transform.scale(BACKGROUND, (SCREEN_WIDTH, SCREEN_HEIGHT))
START_IMAGE = pygame.image.load('assets/sprites/message.png').convert_alpha()

# Create sprite groups
bird_group = pygame.sprite.Group()
bird = Bird()
bird_group.add(bird)

ground_group = pygame.sprite.Group()
for i in range(2):
    ground = Ground(GROUND_WIDTH * i)
    ground_group.add(ground)

pipe_group = pygame.sprite.Group()
for i in range(2):
    pipes = get_random_pipes(SCREEN_WIDTH * i + 800)
    pipe_group.add(pipes[0])
    pipe_group.add(pipes[1])

# Main game loop
clock = pygame.time.Clock()
game_started = False

# Start screen loop
while not game_started:
    clock.tick(15)
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_SPACE or event.key == K_UP:
                bird.bump()
                pygame.mixer.music.load(WING_SOUND_PATH)
                pygame.mixer.music.play()
                game_started = True

    # Draw start screen
    screen.blit(BACKGROUND, (0, 0))
    screen.blit(START_IMAGE, (120, 150))

    # Update ground and bird animations
    if is_off_screen(ground_group.sprites()[0]):
        ground_group.remove(ground_group.sprites()[0])
        new_ground = Ground(GROUND_WIDTH - 20)
        ground_group.add(new_ground)

    bird.begin()
    ground_group.update()

    # Draw sprites
    bird_group.draw(screen)
    ground_group.draw(screen)

    pygame.display.update()

# Main game loop
while True:
    clock.tick(15)
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_SPACE or event.key == K_UP:
                bird.bump()
                pygame.mixer.music.load(WING_SOUND_PATH)
                pygame.mixer.music.play()

    # Draw game screen
    screen.blit(BACKGROUND, (0, 0))

    if is_off_screen(ground_group.sprites()[0]):
        ground_group.remove(ground_group.sprites()[0])
        new_ground = Ground(GROUND_WIDTH - 20)
        ground_group.add(new_ground)

    if is_off_screen(pipe_group.sprites()[0]):
        pipe_group.remove(pipe_group.sprites()[0])
        pipe_group.remove(pipe_group.sprites()[0])
        pipes = get_random_pipes(SCREEN_WIDTH * 2)
        pipe_group.add(pipes[0])
        pipe_group.add(pipes[1])

    # Update sprites
    bird_group.update()
    ground_group.update()
    pipe_group.update()

    # Draw sprites
    bird_group.draw(screen)
    pipe_group.draw(screen)
    ground_group.draw(screen)

    pygame.display.update()

    # Check for collisions
    if (pygame.sprite.groupcollide(bird_group, ground_group, False, False, pygame.sprite.collide_mask) or
            pygame.sprite.groupcollide(bird_group, pipe_group, False, False, pygame.sprite.collide_mask)):
        pygame.mixer.music.load(HIT_SOUND_PATH)
        pygame.mixer.music.play()
        time.sleep(1)
        break