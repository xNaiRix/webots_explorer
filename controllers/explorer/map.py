from typing import List, Tuple
from enum import Enum
import math
from constants import CELL_SIDE

class Direction(str, Enum):
    N = "NORTH"#
    S = "SOUTH"#
    E = "EAST"#
    W = "WEST"#

    @property
    def angle(self) -> float:
        return {
            Direction.N: math.pi/2,
            Direction.S: -math.pi/2,
            Direction.E: 0,
            Direction.W: math.pi
        }[self]

    @staticmethod
    def from_angle(theta:float) -> "Direction":
        direction = [
            Direction.E,
            Direction.N,
            Direction.W,
            Direction.S
        ]
        return direction[round(theta / (math.pi/2)) % 4]

    def get_neighboring(self)->Tuple["Direction", "Direction"]:
        match self:
            case Direction.N:
                return Direction.W, Direction.E
            case Direction.S:
                return Direction.E, Direction.W
            case Direction.E:
                return Direction.N, Direction.S
            case Direction.W:
                return Direction.S, Direction.N

class MapPoint:
    def __init__(self, cell_x, cell_y):#positive Это вправо и вниз
        self.cell_x = cell_x
        self.cell_y = cell_y

    def __hash__(self):
        return hash((self.cell_x, self.cell_y))
    
    def __eq__(self, other:"MapPoint"):
        return self.cell_x == other.cell_x \
            and self.cell_y == other.cell_y
    @staticmethod
    def from_float_coords(x:float, y:float) -> "MapPoint":
        return MapPoint(round(x / CELL_SIDE), round(y / CELL_SIDE))
    
    def distance_to_float_coords(self, x:float, y:float) -> float:
        return math.sqrt((self.cell_x * CELL_SIDE - x) ** 2 + (self.cell_y * CELL_SIDE - y) ** 2)

    def add_relative(self, dx:int, dy:int, direction:Direction)->"MapPoint":#dx, dy - координаты относительно направления
        new_point = MapPoint(self.cell_x, self.cell_y)
        match direction:
            case Direction.N:
                new_point.cell_x +=  dx
                new_point.cell_y +=  dy
            case Direction.E:
                new_point.cell_x +=  dy
                new_point.cell_y += -dx
            case Direction.W:
                new_point.cell_x += -dy
                new_point.cell_y += dx
            case Direction.S:
                new_point.cell_x += -dx
                new_point.cell_y += -dy
            
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
        if 0<= pos.cell_x < self.cell_width and\
           0<= pos.cell_y < self.cell_height:
            self.cells[pos.cell_x][pos.cell_y].unknown = False
            self.cells[pos.cell_x][pos.cell_y].empty = False

    def set_empty(self, pos:MapPoint):
        if 0<= pos.cell_x < self.cell_width and\
           0<= pos.cell_y < self.cell_height:
           self.cells[pos.cell_x][pos.cell_y].unknown = False
           self.cells[pos.cell_x][pos.cell_y].empty = True

    def is_empty(self, pos:MapPoint)->bool|None:#None если черт знает
        if pos.cell_x < 0 or pos.cell_y < 0:
            return False
        if pos.cell_x >= self.cell_width or pos.cell_y >= self.cell_height:
            return False
        return self.cells[pos.cell_x][pos.cell_y].empty
    
    def is_unknown(self, pos:MapPoint)->bool:
        if pos.cell_x < 0 or pos.cell_y < 0:
            return False
        if pos.cell_x >= self.cell_width or pos.cell_y >= self.cell_height:
            return False
        return self.cells[pos.cell_x][pos.cell_y].unknown

    def _odd_robot_can_be_placed(self, pos:MapPoint)->bool|None:#None если черт знает
        i, j = pos.cell_x, pos.cell_y
        r = self.robot_cell_radius
        h = [self.is_empty(MapPoint(x,y)) for x in range(i-r, i+r+1)
                for y in range(j-r-1, j+r+2)]
        h += [self.is_empty(MapPoint(x,y)) for x in (i-r-1, i+r+1)
                for y in range(j-r, j+r+1)]
        return all(h)
    
    def robot_can_be_placed(self, pos:MapPoint)->bool|None:#None если черт знает
        if pos.cell_x < 0 or pos.cell_y < 0:
            return False
        if pos.cell_x >= self.cell_width or pos.cell_y >= self.cell_height:
            return False
        if self.cells[pos.cell_x][pos.cell_y].unknown:
            return None
        return self._odd_robot_can_be_placed(pos)
    

    def is_interesting(self, pos:MapPoint, direction:Direction)->bool:
        if not self.robot_can_be_placed(pos):
            return False
        h = [self.is_unknown(pos.add_relative(dx,dy,direction)) 
             for dx in range(-self.robot_cell_radius-2,self.robot_cell_radius+3)
               for dy in [-self.robot_cell_radius - 1]]
        h += [self.is_unknown(pos.add_relative(dx,dy,direction)) 
              for dx in [ -self.robot_cell_radius - 2,
                          -self.robot_cell_radius - 1,
                          self.robot_cell_radius + 1,
                          self.robot_cell_radius + 2
                          ]
               for dy in range(-self.robot_cell_radius, 1)]
        
        h += [self.is_unknown(pos.add_relative(dx,dy,direction)) 
              for dx in range(-self.robot_cell_radius,self.robot_cell_radius+1)
               for dy in [-self.robot_cell_radius - 2]]
        return any(h)
    
    def print(self):
        for i in range(self.cell_width):
            for j in range(70,130):#self.cell_height):
                cell = self.cells[i][j]
                if cell.unknown:
                    print("?", end=" ")
                elif cell.empty:
                    print(".", end=" ")
                else:
                    print("#", end=" ")
            print()
    def draw_map(self):
        matrix = [["?" for _ in range(self.cell_width)] for _ in range(self.cell_height)]
        for i in range(self.cell_width):
            for j in range(self.cell_height):
                cell = self.cells[i][j]
                if cell.unknown:
                    matrix[i][j] = "?"
                elif cell.empty:
                    matrix[i][j] = "."
                else:
                    matrix[i][j] = "#"
        return matrix
        

        
        

