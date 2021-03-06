#! /usr/bin/env python
__author__ = 'Joris Quenee'

import os
import time
from maze import *
import pygame
from pygame.locals import *
from random import *

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
    pygame.mouse.set_visible(0) # disable mouse cursor
    # pygame.mixer.pre_init(44100, -16, 2, 2048)
    # pygame.mixer.init()
    scr_inf = pygame.display.Info()
    os.environ['SDL_VIDEO_WINDOW_POS'] = '{}, {}'.format(scr_inf.current_w // 2 - WINSIZE[0] // 2,
                                                         scr_inf.current_h // 2 - WINSIZE[1] // 2)
    screen = pygame.display.set_mode(WINSIZE)
    pygame.display.set_caption('Trap')

    clock = pygame.time.Clock()
    maze = draw_maze(screen)

    # by default the key repeat is disabled
    # call set_repeat() to enable it
    # pygame.key.set_repeat(300, 1000) / don't work as expected. replaced by USEREVENT
    
    PLAYER_EVENT, t = pygame.USEREVENT+4, 400 # in millisecond
    pygame.time.set_timer(PLAYER_EVENT, t)

    WOLF_EVENT, t = pygame.USEREVENT+1, 400 # in millisecond
    pygame.time.set_timer(WOLF_EVENT, t)

    MOUSE_EVENT, t = pygame.USEREVENT+2, 300 # in millisecond
    pygame.time.set_timer(MOUSE_EVENT, t)

    TELEPORTATION_EVENT, t = pygame.USEREVENT+3, 10000 # every 10s, we pickup one mouse or wolf in random and we teleport it
    pygame.time.set_timer(TELEPORTATION_EVENT, t)

    done = 0
    threads = []
    while not done:

        for e in pygame.event.get():

            if e.type == pygame.KEYDOWN:
                if e.key == QUIT or e.key == K_ESCAPE:
                    done = 1
                if e.key == K_RETURN:
                    maze = draw_maze(screen) # re-init the game
                    pygame.event.clear() # clear event queue
                #if e.key == K_LEFT or e.key == K_RIGHT or e.key == K_UP or e.key == K_DOWN:
                #    pygame.event.post(pygame.event.Event(PLAYER_EVENT))
                if e.key == K_LEFT:
                    maze.player.move(maze, 'W', screen)
                if e.key == K_RIGHT:
                    maze.player.move(maze, 'E', screen)
                if e.key == K_UP:
                    maze.player.move(maze, 'N', screen)
                if e.key == K_DOWN:
                    maze.player.move(maze, 'S', screen)

            if e.type == TELEPORTATION_EVENT:
                maze.teleportation(screen)

            if e.type == WOLF_EVENT:
                wd = maze.wolf.next_move(maze)
                maze.wolf.move(maze, wd, screen)
            if e.type == MOUSE_EVENT:
                for mouse in maze.mice:
                    if mouse.alive:
                        md = mouse.next_move(maze)
                        mouse.move(maze, md, screen)

            if e.type == PLAYER_EVENT:
                if pygame.key.get_pressed()[K_LEFT]:
                    maze.player.move(maze, 'W', screen)
                if pygame.key.get_pressed()[K_RIGHT]:
                    maze.player.move(maze, 'E', screen)
                if pygame.key.get_pressed()[K_UP]:
                    maze.player.move(maze, 'N', screen)
                if pygame.key.get_pressed()[K_DOWN]:
                    maze.player.move(maze, 'S', screen)


        # Animation	Handling #
        if maze.end_game:
            maze = draw_maze(screen)

        maze.wolf.animation(screen)
        maze.player.animation(screen)
        for mouse in maze.mice:
            if mouse.alive:
                mouse.animation(screen)
        for cheese in maze.cheeses:
            if cheese.state > 0:
                cheese.draw(screen)

        # Collision detections
        maze.wolf_kill_player(screen)
        maze.player_eat_mouse(screen)
        maze.player_eat_cheese(screen)
        maze.mouse_eat_cheese(screen)

     	# FPS / Frame Rate #
        pygame.display.update()
        clock.tick(25)

if __name__ == '__main__':
    main()
