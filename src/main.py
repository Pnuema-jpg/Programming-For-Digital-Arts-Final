#  make a top down map with a moveable player using pygame
import pygame
import sys
import random
from sys import exit
from pygame.locals import QUIT
import math





pygame.init()     
# create window
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Photon Edge")
clock = pygame.time.Clock()
background = pygame.image.load("background.png").convert()


class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill((0, 0, 0, 0))  # Transparent
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.pos = pygame.math.Vector2(400, 300)
        self.image = pygame.image.load("player.png").convert_alpha()
        # Scale the image 1.25x bigger
        original_size = self.image.get_size()
        self.image = pygame.transform.scale(self.image, (int(original_size[0] * 1.25), int(original_size[1] * 1.25)))
        self.base_image = self.image
        self.hitbox = self.image.get_rect(center = self.pos)
        self.rect = self.hitbox.copy()
        self.speed = 2.5
        self.swordbeam_cooldown = 0
        self.swordbeam = False
        self.angle = 0
        self.velocity_x = 0
        self.velocity_y = 0

    def player_rotate(self):
        # Rotate based on movement direction from WASD
        if self.velocity_x != 0 or self.velocity_y != 0:
            self.angle = math.degrees(math.atan2(-self.velocity_y, self.velocity_x))
        # If no movement, keep current angle
        self.image = pygame.transform.rotate(self.base_image, self.angle)
        self.rect = self.image.get_rect(center=self.hitbox.center)
    
    def user_input(self):
        self.velocity_x = 0
        self.velocity_y = 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.velocity_y = -self.speed
            self.velocity_x = 0
        if keys[pygame.K_s]:
            self.velocity_y = self.speed
            self.velocity_x = 0
        if keys[pygame.K_d]:
            self.velocity_x = self.speed
            self.velocity_y = 0
        if keys[pygame.K_a]:
            self.velocity_x = -self.speed
            self.velocity_y = 0

        if pygame.mouse.get_pressed() == (1, 0, 0):
            if self.swordbeam_cooldown == 0:
                self.create_swordbeam()
    
    def create_swordbeam(self):
        if self.swordbeam_cooldown == 0:
            self.swordbeam_cooldown = 50
            self.beam = Beam(self.hitbox.centerx, self.hitbox.centery, self.angle)
            all_sprites.add(self.beam)
            beam_group.add(self.beam)

    def move(self):
        self.pos += pygame.math.Vector2(self.velocity_x, self.velocity_y)
        self.hitbox.center = (round(self.pos.x), round(self.pos.y))
        if pygame.sprite.spritecollide(self, wall_group, False):
            # Undo vertical movement
            self.pos.y -= self.velocity_y
            self.hitbox.center = (round(self.pos.x), round(self.pos.y))
        
        self.rect.center = self.hitbox.center
    def update(self):
        self.user_input()
        self.move()
        self.player_rotate()
        if self.swordbeam_cooldown > 0:
            self.swordbeam_cooldown -= 1
class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__(enemy_group, all_sprites)
        self.image = pygame.image.load("enemy1.png").convert_alpha()
        self.image = pygame.transform.rotozoom(self.image, 0, 1.5)
        self.position = pygame.math.Vector2(pos)
        self.rect = self.image.get_rect(center=self.position)
        self.direction = pygame.math.Vector2()
        self.velocity = pygame.math.Vector2()
        self.speed = 2
        self.shoot_cooldown = 0
        self.shoot_interval = 60  # Shoot every 60 frames (1 second at 60 FPS)

    def chasing(self):
        # Calculate direction to player
        player_vector = pygame.math.Vector2(player1.rect.center)
        distance_vector = player_vector - self.position
        
        # Determine which direction is closest to the player (up, down, left, right)
        abs_x = abs(distance_vector.x)
        abs_y = abs(distance_vector.y)
        
        if abs_x > abs_y:
            # Move left or right
            if distance_vector.x > 0:
                self.direction = pygame.math.Vector2(1, 0)  # Right
            else:
                self.direction = pygame.math.Vector2(-1, 0)  # Left
        else:
            # Move up or down
            if distance_vector.y > 0:
                self.direction = pygame.math.Vector2(0, 1)  # Down
            else:
                self.direction = pygame.math.Vector2(0, -1)  # Up
        
        self.velocity = self.direction * self.speed
        self.position += self.velocity
        self.rect.center = self.position

    def shoot(self):
        # Calculate direction toward player and constrain to 4 directions
        player_vector = pygame.math.Vector2(player1.rect.center)
        distance_vector = player_vector - self.position
        
        # Determine which direction is closest (up, down, left, right)
        abs_x = abs(distance_vector.x)
        abs_y = abs(distance_vector.y)
        
        if abs_x > abs_y:
            # Shoot left or right
            if distance_vector.x > 0:
                angle = 0  # Right
            else:
                angle = 180  # Left
        else:
            # Shoot up or down
            if distance_vector.y > 0:
                angle = -90  # Down
            else:
                angle = 90  # Up
        
        # Create beam
        beam = Beam(self.position.x, self.position.y, angle)
        all_sprites.add(beam)
        beam_group.add(beam)

    def update(self):
        self.chasing()
        
        # Handle shooting
        if self.shoot_cooldown <= 0:
            self.shoot()
            self.shoot_cooldown = self.shoot_interval
        else:
            self.shoot_cooldown -= 1

class Beam(pygame.sprite.Sprite):
    def __init__(self, x,y, angle):
        super().__init__()
        self.spritesheet = pygame.image.load("Beam.png").convert_alpha()
        self.angle = angle
        self.frame = 0
        self.animation_speed = 0.15
        self.frame_width = 32
        self.frame_height = 32
        # Calculate number of frames in sprite sheet
        self.num_frames = self.spritesheet.get_width() // self.frame_width
        self.update_image()
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.center = (self.x, self.y)
        self.speed = 10
        self.velocity = pygame.math.Vector2(self.speed, 0).rotate(-self.angle)
    
    def update_image(self):
        # Extract frame from spritesheet
        frame_x = int(self.frame % self.num_frames) * self.frame_width
        frame_y = 0
        frame_rect = pygame.Rect(frame_x, frame_y, self.frame_width, self.frame_height)
        frame_image = self.spritesheet.subsurface(frame_rect).copy()
        # Scale up 2x before rotating
        frame_image = pygame.transform.scale(frame_image, (self.frame_width * 2, self.frame_height * 2))
        # Rotate the frame
        self.image = pygame.transform.rotate(frame_image, self.angle)
    
    def beam_movement(self):
        self.x += self.velocity.x
        self.y += self.velocity.y
        self.rect.center = (int(self.x), int(self.y))
        
        # Animate frames (loops automatically with modulo)
        self.frame += self.animation_speed
        self.update_image()

    def update(self):
        self.beam_movement()

all_sprites = pygame.sprite.Group()
beam_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
wall_group = pygame.sprite.Group()
player1 = Player()
# Create enemy at random position (avoiding the edges)
enemy_x = random.randint(50, 750)
enemy_y = random.randint(50, 550)
badguy = Enemy((enemy_x, enemy_y))

all_sprites.add(player1)

# Create walls around the edges
walls = [
    Wall(0, 0, 800, 20),      # Top wall
    Wall(0, 580, 800, 20),    # Bottom wall
    Wall(0, 0, 20, 600),      # Left wall
    Wall(780, 0, 20, 600),    # Right wall
]

for wall in walls:
    wall_group.add(wall)



while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    screen.blit(background, (0, 0))
    screen.blit(player1.image, player1.rect)
    
    player1.update()
    pygame.draw.rect(screen, (255, 0, 0), player1.hitbox, 2)
    all_sprites.draw(screen)
    all_sprites.update()
    pygame.display.update()
    clock.tick(60)