import sys, pygame, json
from pygame.locals import *
from random import randint
from pprint import pprint

# set up pygame
pygame.init()

# set up screen data
SCREEN_TITLE = "Missile command"

SCREEN_WIDTH = 1024;
SCREEN_WIDTH_HALF = SCREEN_WIDTH / 2;

SCREEN_HEIGHT = 768;
SCREEN_HEIGHT_HALF = SCREEN_HEIGHT / 2;

# set up the colors
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_RED = (255, 0, 0)
COLOR_GREEN = (0, 255, 0)
COLOR_BLUE = (0, 0, 255)

# set up the window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pygame.display.set_caption(SCREEN_TITLE)

# set up the clock
Clock = pygame.time.Clock()

# set up the aim
aim_surface = pygame.image.load('assets/aim.png').convert_alpha()
aim_rect = aim_surface.get_rect()
# hide the standar cursor
pygame.mouse.set_visible(False)
# center the cursor
pygame.mouse.set_pos((SCREEN_WIDTH_HALF - aim_rect.w / 2, SCREEN_HEIGHT_HALF - aim_rect.h / 2))

# see http://math.stackexchange.com/questions/175896/finding-a-point-along-a-line-a-certain-distance-away-from-another-point
class Missile(object):

    def __init__(self, x1, y1, x2, y2, color, speed=1):
        self.position_src = pygame.math.Vector2(x1, y1)
        self.position_dst = pygame.math.Vector2(x2, y2)
        self.position_head = pygame.math.Vector2(x1, y1)
        # distance and direction you would need to move
        # to go exactly from src to dst
        self.distance = self.position_dst - self.position_src
        self.direction = (self.position_dst - self.position_src).normalize()

        self.points = [(self.position_head.x, self.position_head.y)]
        self.color = color
        self.speed = speed

    def update(self):
        self.position_head += self.speed * self.direction

        if self.direction.x > 0:
            if self.position_head.x < self.position_dst.x or self.position_head.y < self.position_dst.y:
                self.points.append((self.position_head.x, self.position_head.y))
        if self.direction.x < 0:
            if self.position_head.x > self.position_dst.x or self.position_head.y < self.position_dst.y:
                self.points.append((self.position_head.x, self.position_head.y))


missiles = []
for i in range(1, 5):
    missiles.append(
      Missile(randint(0, 1024), 10, randint(0, 1024), 700, COLOR_RED)
    )

def draw_missile():
    for missile in missiles:
        pygame.draw.lines(screen, missile.color, False, missile.points, 2)

def draw_aim():
    mouse_pos = pygame.mouse.get_pos()
    screen.blit(aim_surface, (mouse_pos[0] - aim_rect.w / 2, mouse_pos[1] - aim_rect.h / 2))

# run the game loop
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == MOUSEBUTTONUP:
            mouse_pos = pygame.mouse.get_pos()
            missiles.append(
              Missile(randint(0, 1024), 750, mouse_pos[0], mouse_pos[1], COLOR_BLUE, 4)
            )

    keys = pygame.key.get_pressed()

    for missile in missiles:
        missile.update()

    screen.fill(COLOR_BLACK)
    draw_missile()
    draw_aim()

    pygame.display.flip()

    Clock.tick(60)
