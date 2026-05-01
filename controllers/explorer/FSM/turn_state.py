import math
from state import State
from map import Direction, MapPoint, Map


EPS = 0.01

class TurnState(State):
    def __init__(self, world_map:Map, target_direction:Direction):
        super(world_map)
        self.target_direction = target_direction
        self.was_finished = False

    @property
    def _difference(self, theta):
        return (self.target_direction - theta + math.pi) % (2*math.pi) - math.pi

class TurnLeftState(TurnState):
    def tick(self, x:float, y:float, theta, point:MapPoint, direction:Direction):
        if -EPS < self._difference < 0:
            self.was_finished = True
            return 

class TurnRightState(TurnState):
    pass