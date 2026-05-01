from typing import List, Tuple
from enum import Enum

class Direction(str, Enum):
    N = "NORTH"#
    S = "SOUTH"#
    E = "EAST"#
    W = "WEST"#

class MapPoint:
    def __init__(self, x, y, direction:Direction):#positive Это вправо и вниз
        self.x = x
        self.y = y
        self.direction = direction

    def add_relative(self, dx, dy)->"MapPoint":#dx, dy - координаты относительно направления
        new_point = MapPoint(self.x, self.y, self.direction)
        match self.direction:
            case Direction.N:
                new_point.x +=  dx
                new_point.y +=  dy
            case Direction.E:
                new_point.x += -dy
                new_point.y +=  dx
            case Direction.W:
                new_point.x +=  dy
                new_point.y += -dx
            case Direction.S:
                new_point.x += -dx
                new_point.y += -dy
            
        return new_point        
        

class Cell:
    def __init__(self):
        self.unknown = True
        self.empty = None

class Map:
    def __init__(self, robot_cell_radius):
        self.robot_cell_radius = robot_cell_radius#не считая центр
        self.cells:List[List[Cell]] = []
        self.cell_width = 200
        self.cell_height = 200
        for _ in range(self.cell_width):
            self.cells.append([Cell() for __ in range(self.cell_height)])
            
    def set_wall(self, pos:MapPoint):
        if 0<= pos.x < self.cell_width and\
           0<= pos.y < self.cell_height:
            self.cells[pos.x][pos.y].unknown = False
            self.cells[pos.x][pos.y].empty = False

    def set_empty(self, pos:MapPoint):
        if 0<= pos.x < self.cell_width and\
           0<= pos.y < self.cell_height:
           self.cells[pos.x][pos.y].unknown = False
           self.cells[pos.x][pos.y].empty = True

    def is_empty(self, pos:MapPoint)->bool|None:#None если черт знает
        if pos.x[0] < 0 or pos.y < 0:
            return False
        if pos.x >= self.cell_width or pos.y >= self.cell_height:
            return False
        return self.cells[pos.x][pos.y].empty
    
    def is_unknown(self, pos:MapPoint)->bool:
        if pos[0] < 0 or pos[1] < 0:
            return False
        if pos[0] >= self.cell_width or pos[1] >= self.cell_height:
            return False
        return self.cells[pos[0]][pos[1]].unknown

    def _odd_robot_can_be_placed(self, pos:MapPoint)->bool|None:#None если черт знает
        i, j = pos.x, pos.y
        r = self.robot_cell_radius
        h = [self.is_empty((x,y)) for x in range(i-r, i+r+1)
                for y in range(j-r-1, j+r+2)]
        h += [self.is_empty((x,y)) for x in (i-r-1, i+r+1)
                for y in range(j-r, j+r+1)]
        return all(h)
    def robot_can_be_placed(self, pos:MapPoint)->bool|None:#None если черт знает
        if pos.x < 0 or pos.y < 0:
            return False
        if pos.x >= self.cell_width or pos.y >= self.cell_height:
            return False
        if self.cells[pos.x][pos.y].unknown:
            return None
        return self._odd_robot_can_be_placed(pos)
    

    def is_interesting(self, pos:MapPoint)->bool:
        if not self.robot_can_be_placed(pos):
            return False
        h = [self.is_unknown(pos.add_relative(dx,dy)) 
             for dx in range(-self.robot_cell_radius-2,self.robot_cell_radius+3)
               for dy in [-self.robot_cell_radius - 1]]
        h += [self.is_unknown(pos.add_relative(dx,dy)) 
              for dx in [ -self.robot_cell_radius - 2,
                          -self.robot_cell_radius - 1,
                          self.robot_cell_radius + 1,
                          self.robot_cell_radius + 2
                          ]
               for dy in range(-self.robot_cell_radius, 1)]
        
        h += [self.is_unknown(pos.add_relative(dx,dy)) 
              for dx in range(-self.robot_cell_radius,self.robot_cell_radius+1)
               for dy in [-self.robot_cell_radius - 2]]
        return any(h)
    
        

        
        

