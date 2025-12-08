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
        self.base_image = self.image
        self.hitbox = self.image.get_rect(center = self.pos)
        self.rect = self.hitbox.copy()
        self.speed = 5
        self.swordbeam_cooldown = 0
        self.swordbeam = False

    def player_rotate(self):
        self.mouse_pos = pygame.mouse.get_pos()
        self.x_change = self.mouse_pos[0] - self.pos.x
        self.y_change = self.mouse_pos[1] - self.pos.y
        self.angle = math.degrees(math.atan2(-self.y_change, self.x_change))
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
            self.swordbeam() == True
            self.swordbeamexists = True
        else :
            self.swordbeam() == False
    def swordbeamexists(self):
        if self.swordbeam_cooldown == 0:
            self.swordbeam_cooldown = 20
            beam_spawn = self.pos
            self.beam = Beam(beam_spawn, )

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
    def __init__(self, pos, angle):
        super().__init__()
        self.image = pygame.image.load("Beam.png").convert_alpha()
        self.image = pygame.transform.rotozoom(self.image,0,1)
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.x = x
        self.y = y

        self.speed = 10
        self.angle = angle
        self.velocity = pygame.math.Vector2(self.speed, 0).rotate(-self.angle)
    def beam_movement(self):
        self.x += self.velocity.x
        self.y += self.velocity.y

        self.rect.x = int(self.x)
        self.rect.y = int(self.y)


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
    pygame.draw.rect(screen , (0, 255, 0), player1.rect, 2)
    pygame.display.update()
    clock.tick(60)