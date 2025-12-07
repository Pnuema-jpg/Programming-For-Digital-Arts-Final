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
        self.image = pygame.image.load("player.png").convert_alpha()
        self.pos = pygame.math.Vector2(400, 300)
        self.speed = 5
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
    def move(self):
        self.pos += pygame.math.Vector2(self.velocity_x, self.velocity_y)
    def update(self):
        self.user_input()
        self.move()
    

player1 = Player()
        




while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    screen.blit(background, (0, 0))
    screen.blit(player1.image, player1.pos)
    player1.update()
    pygame.display.update()
    clock.tick(60)