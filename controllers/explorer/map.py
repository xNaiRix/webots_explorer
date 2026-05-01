from typing import List

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
        for cell in range(self.cell_width):
            self.cells.append([Cell() for _ in range(self.cell_height)])
            
    def set_wall(self, cell_ind):
        if 0<= cell_ind[0] < self.cell_width and\
           0<= cell_ind[1] < self.cell_height:
            self.cells[cell_ind[0]][cell_ind[1]].unknown = False
            self.cells[cell_ind[0]][cell_ind[1]].empty = False

    def set_empty(self, cell_ind):
        if 0<= cell_ind[0] < self.cell_width and\
           0<= cell_ind[1] < self.cell_height:
           self.cells[cell_ind[0]][cell_ind[1]].unknown = False
           self.cells[cell_ind[0]][cell_ind[1]].empty = True

    def is_empty(self, cell_ind)->bool|None:#None если черт знает
        if cell_ind[0] < 0 or cell_ind[1] < 0:
            return False
        if cell_ind[0] >= self.cell_width or cell_ind[1] >= self.cell_height:
            return False
        return self.cells[cell_ind[0]][cell_ind[1]].empty
    
    def is_unknown(self, cell_ind)->bool:
        if cell_ind[0] < 0 or cell_ind[1] < 0:
            return False
        if cell_ind[0] >= self.cell_width or cell_ind[1] >= self.cell_height:
            return False
        return self.cells[cell_ind[0]][cell_ind[1]].unknown

    def _odd_robot_can_be_placed(self, cell_ind)->bool|None:#None если черт знает
        i, j = cell_ind
        r = self.robot_cell_radius
        h = [self.is_empty((x,y)) for x in range(i-r, i+r+1)
                for y in range(j-r-1, j+r+2)]
        h += [self.is_empty((x,y)) for x in (i-r-1, i+r+1)
                for y in range(j-r, j+r+1)]
        return all(h)
    def robot_can_be_placed(self, cell_ind)->bool|None:#None если черт знает
        if cell_ind[0] < 0 or cell_ind[1] < 0:
            return False
        if cell_ind[0] >= self.cell_width or cell_ind[1] >= self.cell_height:
            return False
        if self.cells[cell_ind[0]][cell_ind[1]].unknown:
            return None
        return self._odd_robot_can_be_placed(cell_ind)
    

    def is_interesting(self, cell_ind, direction)->bool:
        pass

