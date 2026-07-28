import pygame
import time
import math 
from utils import scale_image

GRASS = scale_image(pygame.image.load("imgs/grass.jpg"),2.5)
TRACK = scale_image(pygame.image.load("imgs/track.png"),0.9)
TRACK_BORDER = scale_image(pygame.image.load("imgs/track-border.png"),0.9)
FINISH = pygame.image.load("imgs/Finish_line.png")
REDBULL_CAR = scale_image(pygame.image.load("imgs/rb22.png"),0.06)
W17_CAR = scale_image(pygame.image.load("imgs/w17.png"),0.06)
WIDTH, HEIGHT = TRACK.get_width(), TRACK.get_height()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Formula 1 Racing Game")


FPS = 60
run = True
clock = pygame.time.Clock()

while run:
    clock.tick(FPS)

    WIN.blit(GRASS, (0,0))
    WIN.blit(TRACK, (0,0))
    WIN.blit(REDBULL_CAR, (0,0))

    pygame.display.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            break

pygame.quit()
