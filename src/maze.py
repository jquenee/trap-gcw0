import random
import pygame
import time
import threading

# Create a maze using the depth-first algorithm described at
# https://scipython.com/blog/making-a-maze/
# Christian Hill, April 2017.

__metaclass__ = type
# DESKTOP SIZE SCREEN
# CELL_WIDTH = 40
# CELL_HIGH = 40
# WALL_THICKNESS = 5
# PLAYER_ZOOM = 20

# GCW ZERO OPTIMAL SIZE SCREEN
CELL_WIDTH = 20
CELL_HIGH = 20
WALL_THICKNESS = 3
PLAYER_ZOOM = 10

def is_present(array, value):
    try:
        i = array.index(value)
        return True
    except:
        return False

class TreePath:
    def __init__(self, cell, parent, dir):
        self.parent_direction = dir
        self.parent = parent
        self.cell = cell
        self.neighbours = []

    def __str__(self):
        return (str(self.cell) + " " + str(self.parent_direction) + " " + str(self.neighbours))

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.cell == other.cell

    def __ne__(self, other):
        return not self.__eq__(other)

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
        # bleu
        self.image.fill((0, 0, 255))
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

class Player:
    def __init__(self, file, x, y):
        self.file = file
        self.x, self.y = x, y
        self.image = pygame.image.load(self.file)
        self.image = pygame.transform.scale(self.image, (PLAYER_ZOOM, PLAYER_ZOOM))
        self.rect = self.image.get_rect()
        self.rect.x = x * Cell.w + Cell.wl * 2
        self.rect.y = y * Cell.h + Cell.wl * 2

    def __str__(self):
        return str(self.__class__) + " ("+ str(self.x) + "," + str(self.y) +")"

    def __repr__(self):
        return self.__str__()

    def refresh(self):
        self.rect.x = self.x * Cell.w + Cell.wl * 2
        self.rect.y = self.y * Cell.h + Cell.wl * 2

    def move(self, maze, direction, screen):
        # check if we found the exit
        if direction == 'E' and self.x == maze.exit.x and self.y == maze.exit.y:
            maze.exit.player_found(maze.player, maze, screen)
            return

        # check if we have wall that block access
        if not maze.cell_at(self.x, self.y).walls[direction]:
            # remove player image from current position
            maze.cell_at(self.x, self.y).fill()
            maze.cell_at(self.x, self.y).draw(screen)
            if direction == 'N':
                self.y = self.y - 1
            if direction == 'S':
                self.y = self.y + 1
            if direction == 'E':
                self.x = self.x + 1
            if direction == 'W':
                self.x = self.x - 1
            # set player image to new position
            self.refresh()
            self.draw(screen)

            # check if wolf kill the Player
            maze.wolf.kill_player(maze.player, maze, screen)

    def draw(self, screen):
        screen.blit(self.image, self.rect)

def yell_wolf():
    sound = pygame.mixer.Sound('assets/wolf.wav')
    channel = sound.play()
    # wait end of sound playing
    while channel.get_busy():
        pygame.time.wait(100)  # ms

class Wolf(Player):

    def __init__(self, file, x ,y):
        super(Wolf, self).__init__(file, x ,y) # Python 2.x adaptation
        self.path_stack = []

    # to avoid PyEval_SaveThread: NULL tstate... in Python 2.x
    def yell(self):
        t = threading.Thread(name='yell', target=yell_wolf)
        t.start()
        t.join()

    def kill_player(self, player, maze, screen):
        if self.x == player.x and self.y == player.y:
            self.draw(screen)
            pygame.display.update()
            self.yell()
            maze.game_over()

    def path_search(self, maze, start, end):
        visited = []
        stack = [start]
        expanded = [False]
        root = TreePath(start, None, None)
        nodes = [root] # list to retrieve the nodes easier
        ndestination = None

        while stack and not ndestination:
            # explore neighbour cells
            if stack and not expanded[-1]:
                cell = stack[-1]
                expanded[-1] = True
                visited += [cell]
                for orientation, wall in cell.walls.items():
                    if not wall:
                        if orientation == 'W':
                            next = maze.cell_at(cell.x - 1, cell.y)
                        if orientation == 'E':
                            next = maze.cell_at(cell.x + 1, cell.y)
                        if orientation == 'N':
                            next = maze.cell_at(cell.x, cell.y - 1)
                        if orientation == 'S':
                            next = maze.cell_at(cell.x, cell.y + 1)
                        if not is_present(visited, next):
                            # print("current to next: " + str(cell) +"-"+ str(next)+" " + orientation)
                            cnode = nodes[nodes.index(TreePath(cell, None, None))] # retrieve current node from current cell
                            nnode = TreePath(next, cnode, orientation) # create the new node (child)
                            cnode.neighbours += [nnode] # attach the child to the parent node
                            nodes += [nnode] # put the new node into the list
                            stack += [next]
                            expanded += [False]
                        # we found the destination. it is not necessary to continue the exploration
                        if next == end:
                            ndestination = nnode
                            break
            # last visited cell
            elif stack and expanded[-1]:
                stack = stack[:-1]
                expanded = expanded[:-1]

        # retieve path by going up from leaf to root
        path = []
        node = ndestination
        while node and node.parent_direction:
            path += [node.parent_direction]
            node = node.parent

        return path

    def next_move(self, maze):
        if self.path_stack == []:
            source = maze.cell_at(self.x, self.y)
            # print("source: " + str(source))
            # choose random cell to go
            destination = maze.random_cell()
            while source == destination:
                destination = maze.random_cell()
            # print("destination: " + str(destination))
            # compute path tree possibility and retrieve path from tree possibility
            self.path_stack = self.path_search(maze, source, destination)
            # print(self.path_stack)
        return self.path_stack.pop()

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

    def is_allowed(self, x, y):
        is_inside = (x >= 0 and x < self.w and y >= 0 and y < self.h)
        is_intoexit = (self.w <= x and self.exit.y == y)
        return is_inside or is_intoexit

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
