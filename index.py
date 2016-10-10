import sys, os, pygame, json
from pygame.locals import *
from random import randint
from pprint import pprint

# set up pygame
pygame.init()

Vector2 = pygame.math.Vector2

# set up screen data
SCREEN_TITLE = "Missile command"

SCREEN_WIDTH = 1024;
SCREEN_WIDTH_HALF = SCREEN_WIDTH / 2;

SCREEN_HEIGHT = 768;
SCREEN_HEIGHT_HALF = SCREEN_HEIGHT / 2;

# set up the colors
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_RED   = (255, 0, 0)
COLOR_GREEN = (0, 255, 0)
COLOR_BLUE  = (0, 0, 255)

# set up the window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pygame.display.set_caption(SCREEN_TITLE)

# set up the clock
Clock = pygame.time.Clock()

# set up assets base dir
ASSETS_BASE_DIR = 'assets/dst/'

# set up the font
# font = pygame.font.Font(None, 24)
font = pygame.font.SysFont("monospace", 15)

# set up land
land_surface = pygame.image.load(os.path.join(ASSETS_BASE_DIR, 'land/land.png')).convert_alpha()

# set up city
city_surface = pygame.image.load(os.path.join(ASSETS_BASE_DIR, 'city/city.png')).convert_alpha()

# set up the aim
aim_surface = pygame.image.load(os.path.join(ASSETS_BASE_DIR, 'aim.png')).convert_alpha()
aim_rect = aim_surface.get_rect()

# set up missiles
missile_surface = pygame.image.load(os.path.join(ASSETS_BASE_DIR, 'missile/missile.png')).convert()
missile_rect = missile_surface.get_rect()

# hide the standar cursor
pygame.mouse.set_visible(False)

# center the cursor
pygame.mouse.set_pos((SCREEN_WIDTH_HALF - aim_rect.w / 2, SCREEN_HEIGHT_HALF - aim_rect.h / 2))

# set up missile lists
missiles_attack = []
missiles_defend = []

# set up missile launcher list
missile_launchers = []

# set up explosions list
explosions = []

# set up explosion images
explosion_frames = [
  pygame.image.load(
    os.path.join(ASSETS_BASE_DIR, 'explosion/explosion-{}.png'.format(i))
  ).convert_alpha() for i in range(0, 4)
]

explosion_frames.extend(list(reversed(explosion_frames)))

class Explosion(object):

    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.__frames = explosion_frames
        self.__frame_idx = 0
        self.__frame_last_idx = len(self.__frames) - 1
        self.frame_current = self.__frames[self.__frame_idx]

        self.__tick_duration = 150
        self.__tick_current = 0
        self.__tick_last = pygame.time.get_ticks()
        self.__tick_accum = 0

    def update(self):

        self.frame_current = self.__frames[self.__frame_idx]

        self.__tick_current = pygame.time.get_ticks()
        self.__tick_accum += self.__tick_current - self.__tick_last

        if self.__tick_accum > self.__tick_duration:

            if self.__frame_idx == self.__frame_last_idx:
                explosions.remove(self)
            else:
                self.__frame_idx += 1

            self.__tick_accum -= self.__tick_duration

        self.__tick_last = self.__tick_current

class Missile(object):

    def __init__(self, missile_type, pos_src, pos_dst, color, speed):

        self.head_surface = pygame.Surface((2, 2))
        pygame.draw.rect(self.head_surface, COLOR_WHITE, self.head_surface.get_rect())

        self.__missile_type = missile_type

        # direction of the missile
        direction = (pos_dst - pos_src).normalize()

        # total distance that missile must travel to reach his target
        self.__distance = pos_dst.distance_to(pos_src)

        # the current distance traveled
        self.__distance_traveled = 0

         # how many the head should move each frame
        self.__step = speed * direction

        # the length of a step
        self.__step_length = self.__step.length()

        self.pos_head = Vector2(pos_src)

        self.path = [
          (pos_src.x, pos_src.y),
          (self.pos_head.x, self.pos_head.y)
        ]

        self.color = color

        # wheter or not a MIRV missile has splitted
        self.__splitted = False

        # a MIRV missile splits when his head is in the middle of
        # his trajectory
        self.__distance_half = self.__distance / 2

    def __can_split(self):
        return all([
          self.__missile_type == 'MIRV',
          self.__distance_traveled > self.__distance_half,
          not self.__splitted
        ])

    def update(self):

        self.__distance_traveled += self.__step_length
        if self.__distance_traveled < self.__distance:
            self.pos_head += self.__step
            self.path.append((self.pos_head.x, self.pos_head.y))
        else:
            self.destroy()

        if self.__can_split():
            missiles_attack.extend([
              create_missile('attack', Vector2(self.pos_head), Vector2(randint(0, 1024), 700)),
              create_missile('attack', Vector2(self.pos_head), Vector2(randint(0, 1024), 700))
            ])

            self.__splitted = True

    def destroy(self):
        if   self.__missile_type in ['attack', 'MIRV']:
            missiles_attack.remove(self)
        elif self.__missile_type == 'defend':
            missiles_defend.remove(self)

        explosions.append(Explosion(self.pos_head.x, self.pos_head.y))

class MissileLauncher(object):

    def __init__(self, pos_src, button):
        self.pos_src = pos_src
        # left button 1
        # middle button 2
        # right button 3
        self.__button = button
        self.missile_count = 10

    def handleInput(self, event):
        if event.type == MOUSEBUTTONUP and event.button == self.__button and self.missile_count > 0:
            missiles_defend.append(
              create_missile('defend', self.pos_src, Vector2(pygame.mouse.get_pos()))
            )

            self.missile_count -= 1

    def destroy(self):
        pass

def create_missile(missile_type, pos_src, pos_dst):
    if   missile_type == 'attack':
        return Missile('attack', pos_src, pos_dst, COLOR_RED, 0.5)
    elif missile_type == 'MIRV':
        return Missile('MIRV', pos_src, pos_dst, COLOR_RED, 0.5)
    elif missile_type == 'defend':
        return Missile('defend', pos_src, pos_dst, COLOR_BLUE, 8)

def check_missile_explosion_collision():
    for missile in missiles_attack:
        for explosion in explosions:
            frame = explosion.frame_current
            frame_rect = frame.get_rect()

            frame_min_x = explosion.x - frame_rect.w / 2
            frame_min_y = explosion.y - frame_rect.h / 2
            frame_max_x = frame_min_x + frame_rect.w
            frame_max_y = frame_min_y + frame_rect.h

            collides = all([
              missile.pos_head.x >= frame_min_x,
              missile.pos_head.x <= frame_max_x,
              missile.pos_head.y >= frame_min_y,
              missile.pos_head.y <= frame_max_y
            ])

            if collides and missile in missiles_attack:
                missiles_attack.remove(missile)

def update_missiles():
    for missile in missiles_attack + missiles_defend:
        missile.update()

def update_explosions():
    for explosion in explosions:
        explosion.update()

def draw_land():
    screen.blit(land_surface, (0, 640))

def draw_cities():
    screen.blit(city_surface, (64, 672))
    screen.blit(city_surface, (192, 672))
    screen.blit(city_surface, (320, 672))
    screen.blit(pygame.transform.flip(city_surface, True, False), (608, 672))
    screen.blit(pygame.transform.flip(city_surface, True, False), (736, 672))
    screen.blit(pygame.transform.flip(city_surface, True, False), (864, 672))

def draw_missiles():
    for missile in missiles_attack + missiles_defend:
        # draw missile trajectory
        pygame.draw.lines(screen, missile.color, False, missile.path, 2)
        # draw missile head
        screen.blit(missile.head_surface, (missile.pos_head.x, missile.pos_head.y))

def draw_aim():
    mouse_pos = pygame.mouse.get_pos()
    screen.blit(aim_surface, (mouse_pos[0] - aim_rect.w / 2, mouse_pos[1] - aim_rect.h / 2))

def draw_explosions():
    for explosion in explosions:
        frame = explosion.frame_current
        frame_rect = frame.get_rect()
        frame_pos = (explosion.x - frame_rect.w / 2, explosion.y - frame_rect.h / 2)

        screen.blit(frame, frame_pos)

def draw_missiles_counters():
    for missile_launcher in missile_launchers:
        text = font.render(str(missile_launcher.missile_count), 1, COLOR_BLACK)
        text_rect = text.get_rect()

        screen.blit(text, (missile_launcher.pos_src.x - text_rect.w / 2, 700))

if __name__ == '__main__':

    # missile launchers
    missile_launchers.extend([
      MissileLauncher(Vector2(32, 640), 1),
      MissileLauncher(Vector2(512, 640), 2),
      MissileLauncher(Vector2(992, 640), 3)
    ])

    missiles_attack.extend([
      create_missile(
        'attack',
        Vector2(randint(0, 1024), 10),
        Vector2(randint(0, 1024), 700)
      ) for _ in range(1, 5)
    ])

    # straight missile
    missiles_attack.append(create_missile('attack', Vector2(10, 10), Vector2(20, 700)))

    # MIRV missile
    missiles_attack.append(create_missile('MIRV', Vector2(randint(0, 1024), 10), Vector2(randint(0, 1024), 700)))

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            for missile_launcher in missile_launchers:
                missile_launcher.handleInput(event)

        check_missile_explosion_collision()

        update_missiles()
        update_explosions()

        screen.fill(COLOR_BLACK)
        draw_land()
        draw_cities()
        draw_missiles()
        draw_missiles_counters()
        draw_explosions()
        draw_aim()
        pygame.display.update()

        Clock.tick(60)
