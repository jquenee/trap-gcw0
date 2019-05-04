#! /usr/bin/env python
__author__ = 'Joris Quenee'

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

    WOLF_EVENT, t = pygame.USEREVENT+1, 400 # in millisecond
    pygame.time.set_timer(WOLF_EVENT, t)

    MOUSE_EVENT, t = pygame.USEREVENT+2, 300 # in millisecond
    pygame.time.set_timer(MOUSE_EVENT, t)

    done = 0
    while not done:

    	# Event Handling #
    	pressed = pygame.key.get_pressed()
        if pressed[QUIT]:
        	done = 1
        if pressed[K_ESCAPE]:
        	done = 1
        if pressed[K_RETURN]:
        	maze = draw_maze(screen)
        if pressed[K_UP]:
        	maze.player.move(maze, 'N', screen)
        elif pressed[K_DOWN]:
        	maze.player.move(maze, 'S', screen)
        elif pressed[K_LEFT]:
        	maze.player.move(maze, 'W', screen)
        elif pressed[K_RIGHT]:
        	maze.player.move(maze, 'E', screen)

        for e in pygame.event.get():
        	if e.type == WOLF_EVENT:
        		wd = maze.wolf.next_move(maze)
        		maze.wolf.move(maze, wd, screen)
        	if e.type == MOUSE_EVENT:
        		for mouse in maze.mice:
        			if mouse.alive:
        				md = mouse.next_move(maze)
        				mouse.move(maze, md, screen)

        # Animation	Handling #
        if maze.end_game:
        	maze = draw_maze(screen)

        maze.wolf.animation(screen)
        maze.player.animation(screen)
        for mouse in maze.mice:
        	if mouse.alive:
        		mouse.animation(screen)

        # Collision detections
        maze.wolf_kill_player(screen)
        maze.player_eat_mouse(screen)
        #maze.player_eat_cheese(screen)
        #maze.mouse_eat_cheese(screen)

     	# FPS / Frame Rate #
        pygame.display.update()
        clock.tick(20)
        # pygame.event.clear() # clear event queue

if __name__ == '__main__':
    main()
