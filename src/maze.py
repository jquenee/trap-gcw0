import random
import pygame
import time
import threading
from sprite import *

# Create a maze using the depth-first algorithm described at
# https://scipython.com/blog/making-a-maze/
# Christian Hill, April 2017.

__metaclass__ = type

class Cell:
    """A cell in the maze.

    A maze "Cell" is a point in the grid which may be surrounded by walls to
    the north, east, south or west.

    """
    # cell sprite size (room + wall)
    # room = 20 / wall = 5
    w, h = CELL_WIDTH, CELL_HIGH
    wl = WALL_THICKNESS

    # A wall separates a pair of cells in the N-S or W-E directions.
    wall_pairs = {'N': 'S', 'S': 'N', 'E': 'W', 'W': 'E'}

    def __init__(self, x, y):
        """Initialize the cell at (x,y). At first it is surrounded by walls."""
        self.x, self.y = x, y
        self.walls = {'N': True, 'S': True, 'E': True, 'W': True}
        # unvisited cell is green as the wall
        self.image = pygame.Surface([self.w - self.wl * 2, self.h - self.wl * 2])
        # green
        self.image.fill((0, 255, 0))
        # shape to draw
        self.rect = self.image.get_rect()
        self.rect.x = (x * self.w) + self.wl
        self.rect.y = (y * self.h) + self.wl

    def __str__(self):
        return "("+ str(self.x) + "," + str(self.y) +")"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __ne__(self, other):
        return not self.__eq__(other)

    def has_all_walls(self):
        """Does this cell still have all its walls?"""
        return all(self.walls.values())

    def knock_down_wall(self, other, wall):
        """Knock down the wall between cells self and other."""
        self.walls[wall] = False
        other.walls[Cell.wall_pairs[wall]] = False
        # visited cell is bleu and the wall as green
        self.fillw(wall)
        other.fill()

    # fill image without wall
    def fill(self):
        self.image = pygame.Surface([self.w - self.wl * 2, self.h - self.wl * 2])
        self.image.fill((0, 0, 255))
        self.rect = self.image.get_rect()
        self.rect.x = (self.x * self.w) + self.wl
        self.rect.y = (self.y * self.h) + self.wl

    # fill image with wall included
    def fillw(self, wall):
        if wall == 'N' or wall == 'S':
            self.image = pygame.Surface([self.w - self.wl * 2, self.h])
        if wall == 'E' or wall == 'W':
            self.image = pygame.Surface([self.w, self.h - self.wl * 2])
        # bleu
        self.image.fill((0, 0, 255))
        # shape to draw inside the surface
        self.rect = self.image.get_rect()
        self.rect.x = (self.x * self.w) + self.wl
        if wall == 'E':
            self.rect.x = (self.x * self.w) + self.wl
        if wall == 'W':
            self.rect.x = (self.x * self.w) - self.wl

        self.rect.y = (self.y * self.h) + self.wl
        if wall == 'N':
            self.rect.y = (self.y * self.h) - self.wl
        if wall == 'S':
            self.rect.y = (self.y * self.h) + self.wl

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Exit(Cell):
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.image = pygame.Surface([self.w, self.h - self.wl * 2])
        self.image.fill((0, 0, 255)) # bleu
        # shape to draw
        self.rect = self.image.get_rect()
        self.rect.x = (x * self.w) + 2 * self.wl
        self.rect.y = (y * self.h) + self.wl

    def player_found(self, player, maze, screen):
        # remove player before to exit game
        maze.cell_at(self.x, self.y).fill()
        maze.cell_at(self.x, self.y).draw(screen)
        pygame.display.update()
        maze.game_over()

def game_over_sound():
    sound = pygame.mixer.Sound('assets/game-over.wav')
    sound.play()

class Maze:
    """A Maze, represented as a grid of cells."""

    def __init__(self, size, ix=0, iy=0):
        """Initialize the maze grid.
        The maze consists of nx x ny cells and will be constructed starting
        at the cell indexed at (ix, iy).

        """
        self.w, self.h = size[0] // Cell.w, size[1] // Cell.h
        self.ix, self.iy = ix, iy
        self.grid = [[Cell(x, y) for y in range(self.h)] for x in range(self.w)]
        self.end_game = False

    def game_over(self):
        t = threading.Thread(name='game-over', target=game_over_sound)
        t.start()
        t.join()
        pygame.time.delay(2000)
        self.end_game = True

    def teleportation(self, screen):
        # pickup active actors
        actors = []
        actors += [self.wolf]
        for mouse in self.mice:
            if mouse.alive:
                actors += [mouse]
        
        # random pickup one actor
        actor = random.choice(actors)

        # teleport
        actor.teleport(screen)


    def wolf_kill_player(self, screen):
        if self.wolf.rect.x - COLLISION_BOX <= self.player.rect.x <= self.wolf.rect.x + COLLISION_BOX and self.wolf.rect.y - COLLISION_BOX <= self.player.rect.y <= self.wolf.rect.y + COLLISION_BOX:
            self.wolf.draw(screen)
            pygame.display.update()
            self.wolf.yell()
            self.game_over()

    def player_eat_mouse(self, screen):
        for mouse in self.mice:
            if mouse.alive and self.player.rect.x == mouse.rect.x and self.player.rect.y == mouse.rect.y:
                self.player.draw(screen)
                pygame.display.update()
                self.player.chewing_mouse()
                mouse.alive = False

    def player_eat_cheese(self, screen):
        for cheese in self.cheeses:
            if cheese.state > 0:
                cheese.eat_me(self.player, screen)

    def mouse_eat_cheese(self, screen):
        for mouse in self.mice:
            if mouse.alive:
                for cheese in self.cheeses:
                    if cheese.state > 0:
                        cheese.eat_me(mouse, screen)

    def cell_at(self, x, y):
        """Return the Cell object at (x,y)."""
        return self.grid[x][y]

    def random_cell(self):
        x = random.randint(0, self.w - 1)
        y = random.randint(0, self.h - 1)
        return self.grid[x][y]

    def draw(self, screen):
        for row in self.grid:
            for cell in row:
                cell.draw(screen)

    def find_valid_neighbours(self, cell):
        """Return a list of unvisited neighbours to cell."""

        delta = [('W', (-1,0)),
                 ('E', (1,0)),
                 ('S', (0,1)),
                 ('N', (0,-1))]
        neighbours = []
        for direction, (dx,dy) in delta:
            x2, y2 = cell.x + dx, cell.y + dy
            if (0 <= x2 < self.w) and (0 <= y2 < self.h):
                neighbour = self.cell_at(x2, y2)
                if neighbour.has_all_walls():
                    neighbours.append((direction, neighbour))
        return neighbours

    def make_maze(self, screen):
        # Total number of cells.
        n = self.w * self.h
        cell_stack = []
        current_cell = self.cell_at(self.ix, self.iy)
        # Total number of visited cells during maze construction.
        nv = 1

        while nv < n:
            neighbours = self.find_valid_neighbours(current_cell)

            if not neighbours:
                # We've reached a dead end: backtrack.
                current_cell = cell_stack.pop()
                continue

            # Choose a random neighbouring cell and move to it.
            direction, next_cell = random.choice(neighbours)
            current_cell.knock_down_wall(next_cell, direction)
            cell_stack.append(current_cell)
            current_cell = next_cell
            # display here the maze building progression
            self.draw(screen)
            pygame.display.update()
            pygame.time.wait(5)
            nv += 1

        # set exit
        self.exit = Exit(self.w - 1, random.randint(0, self.h - 1))
        self.exit.draw(screen)
        # set player
        self.player = Player("assets/player.png", 0, self.iy)
        self.player.draw(screen)

        # set wolf
        starty = random.randint(0, self.h - 1)
        self.wolf = Wolf("assets/wolf.png", self.w - 1, starty)
        self.wolf.draw(screen)
        # set mice
        self.mice = []
        for i in range(3):
            self.mice += [Mouse("assets/mouse.png", random.randint(0, self.w - 1), random.randint(0, self.h - 1))]
            self.mice[i].draw(screen)

        # set cheeses
        self.cheeses = []
        for i in range(5):
            self.cheeses += [Cheese("assets/cheese.png", random.randint(0, self.w - 1), random.randint(0, self.h - 1))]
            self.cheeses[i].draw(screen)