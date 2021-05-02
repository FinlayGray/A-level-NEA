# import necessary libraries
import pygame as pg
import sys
import random
from pygame.locals import *
import time

# initialise pygame
pg.init()
# set up variables
scr_w, scr_h = pg.display.Info().current_w, pg.display.Info().current_h

screen = pg.display.set_mode((scr_w, scr_h))

b = pg.image.load('test_back.png')
pic = pg.transform.scale(b, (scr_w, scr_h))
BASICFONT = pg.font.Font('freesansbold.ttf', 30)
SECONDFONT = pg.font.Font('freesansbold.ttf', 24)
clock = pg.time.Clock()
WHITE = (255, 255, 255)
spike_size = 50
player_size = 75
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
font = pg.font.Font('freesansbold.ttf', 32)
spike = pg.image.load('spike.png')
spike = pg.transform.scale(spike, (spike_size, spike_size))
spike_double = pg.image.load('spike_double.png')
spike_double = pg.transform.scale(spike_double, (spike_size * 2, spike_size))
char_run_0 = pg.image.load('char_run_0_2.png')
player_img_run = pg.transform.scale(char_run_0, (player_size, player_size))
char_run_1 = pg.image.load('char_run_1.png')
player_img_run_1 = pg.transform.scale(char_run_1, (player_size, player_size))
char_jump_1 = pg.image.load('adventurer-jump-00.png')
char_jump_1 = pg.transform.scale(char_jump_1, (player_size, player_size))
char_jump_2 = pg.image.load('adventurer-jump-01.png')
char_jump_2 = pg.transform.scale(char_jump_2, (player_size, player_size))
char_jump_3 = pg.image.load('adventurer-jump-02.png')
char_jump_3 = pg.transform.scale(char_jump_3, (player_size, player_size))
char_jump_4 = pg.image.load('adventurer-jump-03.png')
char_jump_4 = pg.transform.scale(char_jump_4, (player_size, player_size))
char_jump_5 = pg.image.load('adventurer-smrslt-00.png')
char_jump_5 = pg.transform.scale(char_jump_5, (player_size, player_size))
char_jump_6 = pg.image.load('adventurer-smrslt-01.png')
char_jump_6 = pg.transform.scale(char_jump_6, (player_size, player_size))
char_jump_7 = pg.image.load('adventurer-smrslt-02.png')
char_jump_7 = pg.transform.scale(char_jump_7, (player_size, player_size))
char_jump_8 = pg.image.load('adventurer-smrslt-03.png')
char_jump_8 = pg.transform.scale(char_jump_8, (player_size, player_size))
jump_char = [char_jump_1, char_jump_2, char_jump_3, char_jump_4, char_jump_5, char_jump_6, char_jump_7, char_jump_8]
play = False
menu = True
highscore = False

bottom = (3 * (scr_h / 4))
speed = [0, 0]
gravity = 0.2


# main block class
class block:

    def __init__(self, xpos, ypos, size, visibility, image):
        self.xpos = xpos
        self.ypos = ypos
        self.size = size
        self.visibility = visibility
        self.image = image
        self.rect = image.get_rect()
        self.rect.x = xpos
        self.rect.y = ypos

    # draws block to screen
    def draw(self, screen):
        if self.visibility == True:
            screen.blit(self.image, (self.rect.x, self.rect.y - 50))
        else:
            pass


# player class which is a subclass of block
class player(block):
    def __init__(self, xpos, ypos, size, visibility, image, dead, jump):
        super().__init__(xpos, ypos, size, visibility, image)
        self.dead = dead
        self.jump = jump

    def draw(self, screen):
        if self.visibility == True:
            screen.blit(self.image, (self.rect.x, self.rect.y))
        else:
            pass


# Platform class
class platform():
    def __init__(self, x, y, w, h):
        self.rect = pg.Rect(x, y, w, h)

    def draw(self, screen):
        pg.draw.rect(screen, GREEN, self.rect)


# this function is where the main section of the game runs
def main():
    game = True
    speed = [0, 0]
    block_speed = 10
    gravity = 0.5
    jump_index = 0
    run = 0
    count = 0
    score = 0

    plats = []
    bad_blocks = []
    s = block(scr_w, bottom, 25, True, spike)
    # instantiate player
    p = player(200, bottom - player_size, player_size, True, player_img_run, False, False)
    spawn_pos = scr_w + random.randint(0, scr_w)

    base = platform(0, bottom, scr_w, (scr_h - bottom))
    plats.append(base.rect)
    # set up obstacles
    for i in range(4):
        bad_blocks.append(block(spike_size * -1, bottom, spike_size, True, spike))
    distance = int(scr_w / 4)
    double = block(spike_size * -1, bottom, spike_size * 2, True, spike_double)
    bad_blocks.append(double)
    # main while loop
    while game:
        if count >= 100:
            score_add = block_speed * 5
            score += score_add
            score = int(score)
            block_speed *= 1.05

            count = 0
        for event in pg.event.get():
            if event.type == QUIT:
                pg.quit()
                sys.exit()
        # checks if player is dead
        if p.dead == True:
            phrase = 'You scored ' + str(score)
            text = BASICFONT.render(phrase, 1, BLACK)
            screen.blit(text, (scr_w / 5, scr_h / 2))
            pg.display.update()
            time.sleep(2)
            file = open('scores.txt', 'r')
            for i in file.readlines():
                if int(i) < score:
                    file.close()
                    file = open('scores.txt', 'w')
                    file.write(str(score))
            file.close()
            game = False
        # checks if player on platform
        if p.rect.collidelist(plats) != -1:
            speed = [0, 0]
            gravity = 0
            p.jump = False
        else:
            gravity = 0.5
            # checks if player has hit an obstacle
        if p.rect.collidelist(bad_blocks) != -1:
            p.dead = True

        screen.fill(WHITE)
        s.draw(screen)
        for i in bad_blocks:
            i.draw(screen)
        p.draw(screen)
        base.draw(screen)
        keys = pg.key.get_pressed()
        for key in keys:
            if keys[pg.K_SPACE] and p.jump == False:
                speed[1] -= 6
                p.jump = True
            if keys[pg.K_RSHIFT] and p.jump == False:
                p.rect = p.rect.move([0, 1])

        p.rect = p.rect.move(speed)
        speed[1] += gravity
        for i in bad_blocks:
            if i.rect.x <= 0:
                i.rect.x = spawn_pos + random.randint(0, scr_w / 2)
                num = 0
                for j in range(len(bad_blocks)):
                    if i.rect.x in range(bad_blocks[j].rect.x - distance, bad_blocks[j].rect.x + distance):
                        num += 1
                if num >= 2:
                    i.rect.x = spike_size * -1

            i.rect.x -= block_speed

        text = font.render(str(score), True, RED)
        screen.blit(text, (100, 100))
        clock.tick(60)
        pg.display.update()
        count += 1
        if run < 10 and not p.jump:
            p.image = player_img_run_1
            run += 1
        elif run >= 10 and run < 20 and not p.jump:
            p.image = player_img_run
            run += 1
        # uses different images to animate character
        elif p.jump:

            if run < 5:
                jump_index = 0
            elif run <= 5 and run < 10:
                jump_index = 1
            elif run <= 10 and run < 15:
                jump_index = 2
            elif run <= 15 and run < 20:
                jump_index = 3
            elif run <= 20 and run < 25:
                jump_index = 4
            elif run <= 25 and run < 30:
                jump_index = 5
            elif run <= 30 and run < 35:
                jump_index = 6
            elif run <= 35 and run < 40:
                jump_index = 7
            else:
                run = 0
            p.image = jump_char[jump_index]
            run += 1

        else:

            run = 0
            jump_index = 0


# menu loop
while True:
    while menu:
        for event in pg.event.get():
            if event.type == QUIT:
                pg.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_g:
                    play = True
                    menu = False
                if event.key == K_h:
                    highscore = True
                    menu = False
                if event.key == K_q:
                    pg.quit()
                    sys.exit()
        screen.blit(pic, (0, 0))
        phrase = '''Welcome:'''
        text = SECONDFONT.render(phrase, 1, BLACK)
        screen.blit(text, (scr_w * 1 / 2 - 75, scr_h * (1 / 8)))
        phrase = '''Press G to start'''
        text = SECONDFONT.render(phrase, 1, BLACK)
        screen.blit(text, (scr_w * 1 / 2 - 100, scr_h * (3 / 8)))
        phrase = '''Press H to see highscores'''
        text = SECONDFONT.render(phrase, 1, BLACK)
        screen.blit(text, (scr_w * 1 / 2 - 150, scr_h * (4 / 8)))
        phrase = '''Press Q to quit'''
        text = SECONDFONT.render(phrase, 1, BLACK)
        screen.blit(text, (scr_w * 1 / 2 - 100, scr_h * (5 / 8)))
        pg.display.update()

    while play:
        for event in pg.event.get():
            if event.type == QUIT:
                pg.quit()
                sys.exit()
        main()
        menu = True
        play = False

    while highscore:
        for event in pg.event.get():
            if event.type == QUIT:
                pg.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_b:
                    menu = True
                    highscore = False

        screen.blit(pic, (0, 0))
        file = open('scores.txt', 'r')
        for i in file.readlines():
            phrase = '''The highscore is ''' + i.strip('\n')

        file.close()
        text = SECONDFONT.render(phrase, 1, BLACK)
        screen.blit(text, (scr_w * 1 / 2 - 150, scr_h * (4 / 8)))
        phrase = 'Press B to go back'
        text = SECONDFONT.render(phrase, 1, BLACK)
        screen.blit(text, (0, scr_h * (19 / 20)))

        pg.display.update()
