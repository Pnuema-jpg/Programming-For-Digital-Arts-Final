#  make a top down map with a moveable player using pygame
import pygame
import sys
import random
from sys import exit
from pygame.locals import QUIT
import math










class Player(pygame.sprite.Sprite):
    def __init__(self):
        



pygame.init()
# create window
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Photon Edge")
clock = pygame.time.Clock()

background = pygame.image.load("background.png").convert()

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    screen.blit(background, (0, 0))
    pygame.display.update()
    clock.tick(60)