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
        self.rect.center = self.hitbox.center
    def update(self):
        self.user_input()
        self.move()
        self.player_rotate()
        if self.swordbeam_cooldown > 0:
            self.swordbeam_cooldown -= 1

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

    
player1 = Player()
        
all_sprites = pygame.sprite.Group()
beam_group = pygame.sprite.Group()
all_sprites.add(player1)



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