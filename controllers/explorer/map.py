from typing import List

class Cell:
    def __init__(self):
        self.unknown = True
        self.empty = None

class Map:
    def __init__(self, robot_cell_width):
        self.robot_cell_width = robot_cell_width
        self.cells:List[List[Cell]] = []
        self.cell_width = 200
        self.cell_height = 200
        for cell in range(self.cell_width):
            self.cells.append([])
            for cell in range(self.cell_height):
                self.cells[cell].append(Cell())
            
    def set_wall(self, cell_ind):
        if 0<= cell_ind[0] < self.cell_width and 0 <= cell_ind[1] < self.cell_height:
            self.cells[cell_ind[0]][cell_ind[1]].unknown = False

    def robot_can_be_placed(self, cell_ind):
        pass
    
    def is_interesting(self, cell_ind):
        pass

