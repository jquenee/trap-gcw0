#! /usr/bin/env python
__author__ = 'Joris Quenee'


# TODO:
# Add exit
# Add exit sound ?..
# Clean the code
# Add mouse

import os
import time
from maze import *
import pygame
from pygame.locals import *
from random import *

# 320 x 240
# https://wiki.dingoonity.org/index.php?title=Dingux:OpenDingux:Development#Building_OpenDingux_from_sources

# DESKTOP SIZE SCREEN
WIDTH = 20
HIGH = 10

# GCW ZERO OPTIMAL SIZE SCREEN
WIDTH = 16
HIGH = 12

WINSIZE = (Cell.w * WIDTH, Cell.h * HIGH)

def draw_maze(screen):
    # green is background
    screen.fill((0, 255, 0))
    # start point
    starty = randint(0, HIGH - 1)
    # build the maze
    maze = Maze(WINSIZE, 0, starty)
    maze.make_maze(screen)
    return maze

def main():
    pygame.init()
    pygame.mouse.set_visible(0)
    # pygame.mixer.pre_init(44100, -16, 2, 2048)
    # pygame.mixer.init()
    scr_inf = pygame.display.Info()
    os.environ['SDL_VIDEO_WINDOW_POS'] = '{}, {}'.format(scr_inf.current_w // 2 - WINSIZE[0] // 2,
                                                         scr_inf.current_h // 2 - WINSIZE[1] // 2)
    screen = pygame.display.set_mode(WINSIZE)
    pygame.display.set_caption('Trap')

    clock = pygame.time.Clock()
    maze = draw_maze(screen)

    PNG_EVENT, t = pygame.USEREVENT+1, 300 # in millisecond
    pygame.time.set_timer(PNG_EVENT, t)

    done = 0
    while not done:
        for e in pygame.event.get():
            if e.type == QUIT: # select key in GCW Zero
                done = 1
            if e.type == KEYUP and e.key == K_ESCAPE: # "select" key in GCW Zero
                done = 1
            if e.type == KEYUP and e.key == K_RETURN: # "start" key in GCW Zero
                maze = draw_maze(screen)
            if e.type == KEYUP and e.key == K_UP:
                maze.player.move(maze, 'N', screen)
            if e.type == KEYUP and e.key == K_DOWN:
                maze.player.move(maze, 'S', screen)
            if e.type == KEYUP and e.key == K_LEFT:
                maze.player.move(maze, 'W', screen)
            if e.type == KEYUP and e.key == K_RIGHT:
                maze.player.move(maze, 'E', screen)

            if e.type == PNG_EVENT:
                wd = maze.wolf.next_move(maze)
                maze.wolf.move(maze, wd, screen)

        if maze.end_game:
            maze = draw_maze(screen)

        pygame.display.update()
        clock.tick()

if __name__ == '__main__':
    main()
