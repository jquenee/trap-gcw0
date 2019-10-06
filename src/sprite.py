import random
import pygame
import time
import threading
from gconstants import *

__metaclass__ = type

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

class Sprite:
    def __init__(self, file, x, y):
        self.file = file
        self.x, self.y = x, y
        self.xold, self.yold = x, y
        self.image = pygame.image.load(self.file)
        self.image = pygame.transform.scale(self.image, (SPRITE_ZOOM, SPRITE_ZOOM))
        self.rect = self.image.get_rect()
        self.rect.x = x * CELL_WIDTH + WALL_THICKNESS * 2
        self.rect.y = y * CELL_HIGH + WALL_THICKNESS * 2
        self.blank = pygame.Surface([self.image.get_rect().size[0], self.image.get_rect().size[1]])
        self.blank.fill((0, 0, 255)) # bleu

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Cheese(Sprite):
    def __init__(self, file, x, y):
        super(Cheese, self).__init__(file, x ,y) # Python 2.x adaptation
        self.state = 3 # 3 whole cheese, 2 ate partially, 1 crumb, 0 no left
        self.freeze = 0 

    def update_state(self):
        if self.state == 3:
            self.image = pygame.image.load("assets/cheese.png")
        if self.state == 2:
            self.image = pygame.image.load("assets/cheese-ate.png")
        if self.state == 1:
            self.image = pygame.image.load("assets/cheese-crumb.png")
        if self.state <= 0:
            self.image.fill((0, 0, 255)) # bleu
        self.image = pygame.transform.scale(self.image, (SPRITE_ZOOM, SPRITE_ZOOM))

    def eat_me(self, eater, screen):
        # wolf don't eat cheese
        if type(eater) is not Wolf:
            if self.x == eater.x and self.y == eater.y:
                if self.freeze <= 0:
                    if type(eater) is Player:
                        self.state = 0 # player eat cheese in one time
                    if type(eater) is Mouse:
                        self.state -= 1 # mouse eat cheese piece by piece
                    self.update_state()
                    self.draw(screen)
                    pygame.display.update()
                    eater.chew()
                    self.freeze = 10 # disable hit box during 10 frames
                else:
                    self.freeze -= 1

def player_chewing_mouse():
    sound = pygame.mixer.Sound('assets/player-eat-mouse.wav')
    channel = sound.play()

def player_swallow_cheese():
    sound = pygame.mixer.Sound('assets/player-eat-cheese.wav')
    channel = sound.play()

class Player(Sprite):
    def __init__(self, file, x, y):
        super(Player, self).__init__(file, x ,y) # Python 2.x adaptation
        self.frame = 0

    def __str__(self):
        return str(self.__class__) + " ("+ str(self.x) + "," + str(self.y) +")"

    def __repr__(self):
        return self.__str__()

    # to avoid PyEval_SaveThread: NULL tstate... in Python 2.x
    def chewing_mouse(self):
        t = threading.Thread(name='chewing_mouse', target=player_chewing_mouse)
        t.start()
        t.join()

    def chew(self):
        t = threading.Thread(name='swallow_cheese', target=player_swallow_cheese)
        t.start()
        t.join()

    def erase(self, screen):
        screen.blit(self.blank, self.rect)

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def refresh(self):
        # target reached, resync the position
        if self.frame > FRAME - 1:
            self.rect.x = self.x * CELL_WIDTH + WALL_THICKNESS * 2
            self.rect.y = self.y * CELL_HIGH + WALL_THICKNESS * 2
            return
        # skip previous animation, to jump on the second one
        if self.frame == 0:
            self.xmove, self.ymove = 0, 0
            self.rect.x = self.xold * CELL_WIDTH + WALL_THICKNESS * 2
            self.rect.y = self.yold * CELL_HIGH + WALL_THICKNESS * 2
            xgap = self.rect.x - (self.x * CELL_WIDTH + WALL_THICKNESS * 2)
            ygap = self.rect.y - (self.y * CELL_HIGH + WALL_THICKNESS * 2)
            if xgap != 0:
                self.xmove = xgap / FRAME
            if ygap != 0:
                self.ymove = ygap / FRAME
        self.rect.x -= self.xmove
        self.rect.y -= self.ymove
        self.frame += 1

    def no_frame(self):
        self.rect.x = self.x * CELL_WIDTH + WALL_THICKNESS * 2
        self.rect.y = self.y * CELL_HIGH + WALL_THICKNESS * 2

    def move(self, maze, direction, screen):
        if direction == None:
            return
        # check if we found the exit
        if direction == 'E' and self.x == maze.exit.x and self.y == maze.exit.y:
            maze.exit.player_found(maze.player, maze, screen)
            return

        # check if we have wall that block access
        if not maze.cell_at(self.x, self.y).walls[direction]:
            self.xold = self.x
            self.yold = self.y
            if direction == 'N':
                self.y = self.y - 1
            if direction == 'S':
                self.y = self.y + 1
            if direction == 'E':
                self.x = self.x + 1
            if direction == 'W':
                self.x = self.x - 1

            self.frame = 0 # re-init frame counter

    def animation(self, screen):
        self.erase(screen)
        self.refresh()
        #self.no_frame()
        self.draw(screen)

def yell_wolf():
    sound = pygame.mixer.Sound('assets/wolf.wav')
    channel = sound.play()
    # wait end of sound playing
    while channel.get_busy():
        pygame.time.wait(100)  # ms

def teleport_sound():
    sound = pygame.mixer.Sound('assets/teleportation.wav')
    channel = sound.play()

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

        self.path_stack = path

class Wolf(Player):

    def __init__(self, file, x ,y):
        super(Wolf, self).__init__(file, x ,y) # Python 2.x adaptation
        self.path_stack = []
        self.path_compting_thread = threading.Thread(target=path_search)
        
    # to avoid PyEval_SaveThread: NULL tstate... in Python 2.x
    def yell(self):
        t = threading.Thread(name='yell', target=yell_wolf)
        t.start()
        t.join()

    def vanish_sound(self):
        t = threading.Thread(name='teleport_sound', target=teleport_sound)
        t.start()
        t.join()

    def teleport(self, screen):
        self.erase(screen)
        self.x, self.y = random.randint(0, WIDTH - 1), random.randint(0, HIGH - 1) # pickup random position
        self.refresh()
        self.draw(screen)
        self.path_stack = [] # re-init the path
        self.vanish_sound()

    def next_move(self, maze):
        if self.path_stack == [] and not self.path_compting_thread.is_alive():
            source = maze.cell_at(self.x, self.y)
            # print("source: " + str(source))
            # choose random cell to go
            destination = maze.random_cell()
            while source == destination:
                destination = maze.random_cell()
            # print("destination: " + str(destination))
            # compute path tree possibility and retrieve path from tree possibility
            # new thread is created to avoid lag issue
            self.path_compting_thread = threading.Thread(target=path_search, args=[self, maze, source, destination])
            self.path_compting_thread.start()
            # print(self.path_stack)
        if self.path_stack == []:
            return None
        return self.path_stack.pop()

def mouse_nibble_cheese():
    sound = pygame.mixer.Sound('assets/mouse-eat.wav')
    channel = sound.play()

class Mouse(Wolf):
    def __init__(self, file, x ,y):
        super(Mouse, self).__init__(file, x ,y) # Python 2.x adaptation
        self.alive = True

    def chew(self):
        t = threading.Thread(name='nibble_cheese', target=mouse_nibble_cheese)
        t.start()
        t.join()

''' Orginal game mouse doesn't go directly to cheese
    def next_move(self, maze):
        if self.path_stack == []:
            source = maze.cell_at(self.x, self.y)
            # choose random cheese to go
            cheese = random.choice(maze.cheeses)
            destination = maze.cell_at(cheese.x, cheese.y)
            self.path_stack = self.path_search(maze, source, destination)
            # print(self.path_stack)
        return self.path_stack.pop()
'''
