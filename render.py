# This module will use ray tracing to render a 3d object on a 2d plane. 

import pygame
from pygame.locals import *
# import pandas as pd
from math import *
import random

ES = 5.1
SO = 5
SCALE = 100
HEIGHT = 1080 - 100
WIDTH = 1920 - 100

class Point:
    def __init__(self, name, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.name = name
        self.u = ES*self.x/(ES + SO + self.y) 
        self.v = self.z*ES/(ES + SO + self.y)

    def __truediv__(self, k):
        return Point(self.name, self.x/k, self.y/k, self.z/k )
    
    def __add__(self, other):
        return Point(self.name + other.name, self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Point(self.name + other.name, self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __mul__(self, k):
        return Point(self.name, self.x*k, self.y*k, self.z*k )
    
    def dist(self, other):
        return ((self.x - other.x)**2 + (self.y - other.y)**2 + (self.z - other.z)**2) ** 0.5
    
    def midpoint(self, other):
        return Point(self.name + other.name + '_mid', (self.x + other.x)/2, (self.y + other.y)/2, (self.z + other.z)/2)
    
    def shrink_and_replace(self, other):
        # Given two points, return another two points such that the distance between those points is exactly 1/2 the distance between input points and 
        # the midpoint of the two points is the midpoint of the input points
        mid = self.midpoint(other)
        d = self.dist(other)
        print(mid, d)
        return Point(self.name + other.name + '_shrunk', mid.x - d/4, mid.y - d/4, mid.z - d/4), Point(self.name + other.name +'_shrunk', mid.x + d/4, mid.y + d/4, mid.z + d/4)

    def update(self, dx=0, dy=0, dz=0, x_rot=0, y_rot=0, z_rot=0, sc=1):
        # Displacement
        self.x += dx
        self.y += dy
        self.z += dz

        # Scaling
        self.x *= sc
        self.y *= sc
        self.z *= sc
        
        # Rotation about x-axis
        old_y, old_z = self.y, self.z
        self.y = old_y * cos(x_rot) + old_z * sin(x_rot)
        self.z = -old_y * sin(x_rot) + old_z * cos(x_rot)

        # Rotation about y-axis
        old_x, old_z = self.x, self.z
        self.x = old_x * cos(y_rot) + old_z * sin(y_rot)
        self.z = -old_x * sin(y_rot) + old_z * cos(y_rot)

        # Rotation about z-axis
        old_x, old_y = self.x, self.y
        self.x = old_x * cos(z_rot) + old_y * sin(z_rot)
        self.y = -old_x * sin(z_rot) + old_y * cos(z_rot)

        # 2D-3D Mapping
        self.u = ES*self.x/(ES + SO + self.y) + WIDTH/SCALE/2
        self.v = self.z*ES/(ES + SO + self.y) + HEIGHT/SCALE/2
    
    def __str__(self) -> str:
        return f'({self.name}, {self.x}, {self.y}, {self.z})'
    
    def __repr__(self) -> str:
        return "Point" + str(self)
    
    def to_tuple(self) -> tuple:
        return (self.u* SCALE, self.v * SCALE)
    
    def copy(self):
        res = Point(self.name, self.x, self.y, self.z)
        return res

class Object3D:
    def __init__(self, filename = None, points = None):
        if points is None:
            points = {}
        if filename:
            # table = pd.read_csv(filename, index_col="args")
            # self.filename = filename

            # curr, curr_name = [], ""
            # for c in table:
            #     if "Unnamed" in c:
            #         points[curr_name] = curr
            #         curr, curr_name = [], ""
            #     else:
            #         curr_name += c
            #         curr.append(Point(c, *table[c]))
            # points[curr_name] = curr
            points = self.txt_filename(filename)
        self.color = (0,0,255)
        self.thickness = 1
        self.points = points
        self.modded = False
        self.highlighted = False
        self.visible = {x for x in self.points if 'ref' not in x and x != 'center'}
    
    def txt_filename(self, filename):
        with open(filename) as f:
            data = f.read()
            f.close()

            rows = [line.split(',') for line in data.split("\n")]
            points = {}
            n = len(rows[0])
            curr, curr_name = [], ""
            for i in range(n):
                if i == 0:
                    continue
                name, e1, e2, e3 = (rows[j][i] for j in range(len(rows)))
                if name == "":
                    points[curr_name] = curr
                    curr, curr_name = [], ""
                else:
                    curr.append(Point(name, float(e1), float(e2), float(e3)))
                    curr_name += name
            return points

    def update(self, dx=0, dy=0, dz=0, x_rot=0, y_rot=0, z_rot=0, sc=1):
        for section in self.points.values():
            for point in section:
                point.update(dx, dy, dz, x_rot, y_rot, z_rot, sc)
    
    def highlight(self):
        self.highlighted = not self.highlighted

    def display(self, screen, hl = False):
        for section_name, section in self.points.items():
            if section_name not in self.visible:
                continue
            if hl:
                pygame.draw.lines(screen, (255,255,255), True, [p.to_tuple() for p in section], width=5)
            else:
                pygame.draw.lines(screen, self.color, True, [p.to_tuple() for p in section], width=self.thickness)
    def __str__(self):
        return str(self.points)

    def __repr__(self) -> str:
        return "Object3D(" + str(self) + ")"
    
    def copy(self):
        points =  [list(map(Point.copy, section)) for section in self.points.values()]
        new = Object3D(self.filename)
        new.points = points
        return new
    
def visualize(objs):
    pygame.init()

    FPS = 60

    FramePerSec = pygame.time.Clock()

    surface = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Render")
    moving = False
    prev = 0,0
    while True:
        # pygame.mouse.set_pos(WIDTH // 2, HEIGHT // 2)
        # print(f'{prev=}')
        dx, dy, dz, x_rot, y_rot, z_rot, sc = 0,0,0,0,0,0,1
        FramePerSec.tick(FPS)
        # obj = random.choice(objects_3d)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                    moving = True
            if event.type == pygame.MOUSEBUTTONUP:
                moving = False
            if event.type == pygame.MOUSEMOTION and moving:
                m_x, m_y = event.pos
                # print(m_x, m_y)
                if m_x < prev[0]:
                    m_x = 0.1
                elif m_x >= prev[0]:
                    m_x = -0.1
                if m_y < prev[1]:
                    m_y = -0.1
                elif m_y >= prev[1]:
                    m_y = 0.1
                z_rot = m_x/3
                x_rot = m_y/3
            if event.type == pygame.MOUSEWHEEL:
                sc += event.y / 100

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            dy -= 1
        if keys[pygame.K_s]:
            dy += 1
        if keys[pygame.K_d]:
            dx -= 1
        if keys[pygame.K_a]:
            dx += 1
        if keys[pygame.K_LSHIFT] and keys[pygame.K_UP]:
            dz -= 1
        if keys[pygame.K_LSHIFT] and keys[pygame.K_DOWN]:
            dz += 1

        prev = pygame.mouse.get_pos()
        surface.fill((255,255,255))
        for i, object_3d in enumerate(objs):
            object_3d.update(dx, dy, dz, x_rot, y_rot, z_rot, sc)
            object_3d.display(surface)
        pygame.display.flip()
        pygame.display.update()

def main():
    cube = Object3D("objects_3d/cube.txt")
    visualize([cube])
if __name__ == "__main__":
    main()