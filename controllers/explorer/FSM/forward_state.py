import math
from FSM.state import State
from map import Direction, MapPoint, Map
from constants import CELL_SIDE

EPS = 0.1

class ForwardState(State):
    def __init__(self, world_map:Map, target_point:MapPoint):
        super().__init__(world_map)
        self.target_point = target_point
        self.was_finished = False

    def _difference(self, x:float, y:float, point:MapPoint, direction:Direction) -> float:
        match direction:
            case Direction.N:
                if self.target_point.cell_x == point.cell_x:
                    return self.target_point.cell_y * CELL_SIDE - y
                else:
                    return float('inf')
            case Direction.S:
                if self.target_point.cell_x == point.cell_x:
                    return -(self.target_point.cell_y * CELL_SIDE - y)
                else:
                    return float('inf')
            case Direction.E:
                if self.target_point.cell_y == point.cell_y:
                    return self.target_point.cell_x * CELL_SIDE - x
                else:
                    return float('inf')
            case Direction.W:
                if self.target_point.cell_y == point.cell_y:
                    return -(self.target_point.cell_x * CELL_SIDE - x)
                else:
                    return float('inf')

    def is_finished(self, x:float, y:float, theta:float, point:MapPoint, direction:Direction) -> bool:
        return -EPS < self._difference(x, y, point, direction) <= 0

    def tick(self, x:float, y:float, theta:float, point:MapPoint, direction:Direction):
        if self._difference(x, y, point, direction) > 0:
            return (50.0, 50.0)
        if self._difference(x, y, point, direction) <= -EPS:
            return (-50.0, -50.0)
        return (0.0, 0.0)