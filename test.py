import pygame
import sys

pygame.init()

screen = pygame.display.set_mode((850, 850))
pygame.display.set_caption("TEST")

clock = pygame.time.Clock()

running = True

while running:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

    screen.fill((235, 235, 235))

    pygame.display.flip()

    clock.tick(60)

pygame.quit()

sys.exit()
