import time
import curses
import math
import numpy
import png
import sys

class AStar:
    def __init__(self):
        self.running = True
        self.wall = 'X'
        self.startpoint = self.endpoint = (-1, -1) # x, y

    def run(self, window):
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)
        # render map
        self._read_map()
        for y in range(self.size):
            window.addstr(y, 0, ' '.join(self.map[y]), curses.color_pair(1))
        window.refresh()
        window.getch()
        while (self.running):
            path = self._explore_path()
            #print(path)
            for i in range(len(path)):
                window.addstr(path[i][1], path[i][0] * 2, 'O', curses.color_pair(2))
                window.refresh()
                time.sleep(.2)

            window.getch()
            self.running = False

    def _read_map(self):
        # open png file and read pixel data into array
        pngdata = png.Reader(filename="map.png").asDirect()
        img_bytes = numpy.vstack(list(map(numpy.uint32, pngdata[2])))
        pixels = []
        for y in range(len(img_bytes)):
            temp = []
            # 4 channels for each pixel, RGBA
            for x in range(0, len(img_bytes[0]), 4):
                # skip alpha channel
                temp.append(img_bytes[y][x] << 16 | img_bytes[y][x+1] << 8 | img_bytes[y][x+2] << 0)
            pixels.append(temp)

        start = 0xff0000
        end = 0x0000ff
        wall = 0xff00ff
        space = 0xffffff

        self.size = len(pixels)
        self.map = [[0 for i in range(self.size)] for j in range(self.size)]
        self.nodes = [[None for i in range(self.size)] for j in range(self.size)]
        for y in range(len(pixels)):
            for x in range(len(pixels[0])):
                color = pixels[y][x]
                if color == start:
                    self.startpoint = (x, y)
                    self.map[y][x] = 'S'
                elif color == end:
                    self.endpoint = (x, y)
                    self.map[y][x] = 'E'
                elif color == wall:
                    self.map[y][x] = self.wall
                elif color == space:
                    self.map[y][x] = ' '

        # add starting node
        dist = self._dist(self.startpoint, self.endpoint)
        self.nodes[self.startpoint[1]][self.startpoint[0]] = Node(0.0, dist, False)

    def _explore_path(self):
        # find new node to evaluate
        pos = (-1, -1)
        for y in range(self.size):
            for x in range(self.size):
                if not self.nodes[y][x] is None:
                    if self.nodes[y][x].evaluated == False:
                        if pos[0] >= 0:
                            if self.nodes[y][x].f < self.nodes[pos[1]][pos[0]].f:
                                pos = (x, y)
                            elif self.nodes[y][x].f == self.nodes[pos[1]][pos[0]].f:
                                if self.nodes[y][x].h < self.nodes[pos[1]][pos[0]].h:
                                    pos = (x, y)
                        else:
                            pos = (x, y)
        # evaluate new node
        if pos != self.endpoint and pos[0] >= 0:
            self.nodes[pos[1]][pos[0]].evaluated = True
            for y in range(-1, 2):
                for x in range(-1, 2):
                    if x == y and x == 0:
                        continue
                    mapX = pos[0] + x
                    mapY = pos[1] + y
                    if mapX < 0 or mapY < 0 or mapX >= self.size or mapY >= self.size:
                        continue
                    elif self.map[mapY][mapX] == self.wall:
                        continue
                    newG = 1.0
                    if (x + y) % 2 == 0:
                        newG = math.sqrt(2)
                    newG += self.nodes[pos[1]][pos[0]].g
                    if self.nodes[mapY][mapX] is None:
                        self.nodes[mapY][mapX] = Node(newG, self._dist(pos, self.endpoint), False)
                    elif newG < self.nodes[mapY][mapX].g:
                        self.nodes[mapY][mapX].update_g(newG)
            return self._explore_path()
        else:
            # path to end point is found, add the surrounding node with lowest g value, starting from end point
            return_list = [self.endpoint]
            while pos != self.startpoint:
                temp = (-2, -2)
                for y in range(-1, 2):
                    for x in range(-1, 2):
                        if x == y and x == 0:
                            continue
                        mapX = pos[0] + x
                        mapY = pos[1] + y
                        if mapX < 0 or mapY < 0 or mapX >= self.size or mapY >= self.size:
                            continue
                        elif self.map[mapY][mapX] == self.wall or self.nodes[mapY][mapX] is None:
                            continue
                        if temp[0] < -1:
                            temp = (x, y)
                        elif self.nodes[mapY][mapX].g < self.nodes[pos[1]+temp[1]][pos[0]+temp[0]].g:
                            temp = (x, y)
                pos = (pos[0]+temp[0], pos[1]+temp[1])
                return_list.insert(0, pos)
            return return_list

    def _dist(self, a, b):
        return math.sqrt((b[1] - a[1])**2 + (b[0] - a[0])**2)

class Node:
    def __init__(self, g, h, evaluated):
        self.g = g # discovered path distance from start node
        self.h = h # heuristic distance to end node
        self.f = g + h # sum of the two
        self.evaluated = evaluated

    def update_g(self, newG):
        self.g = newG
        self.f = self.g + self.h

curses.wrapper(AStar().run)
