import math
from state import State
from map import Direction, MapPoint, Map


EPS = 0.01

class TurnState(State):
    def __init__(self, world_map:Map, target_direction:Direction):
        super(world_map)
        self.target_direction = target_direction
        self.was_finished = False

    def _difference(self, theta):
        return (self.target_direction.angle - theta + math.pi) % (2*math.pi) - math.pi

class TurnLeftState(TurnState):
    def is_finished(self, x:float, y:float, theta:float, point:MapPoint, direction:Direction) -> bool:
        return -EPS < self._difference(theta) <= 0

    def tick(self, x:float, y:float, theta:float, point:MapPoint, direction:Direction):
        if not self.is_finished(x, y, theta, point, direction):
            return (-1.0, 1.0)
        return (0.0, 0.0)

class TurnRightState(TurnState):
    def is_finished(self, x:float, y:float, theta:float, point:MapPoint, direction:Direction) -> bool:
        return 0 <= self._difference(theta) < EPS

    def tick(self, x:float, y:float, theta:float, point:MapPoint, direction:Direction):
        if not self.is_finished(x, y, theta, point, direction):
            return (1.0, -1.0)
        return (0.0, 0.0)