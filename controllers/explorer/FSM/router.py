from typing import List
from map import Direction, MapPoint, Map

class State:
    def __init__(self, point:MapPoint, direction:Direction):
        self.point = point
        self.direction = direction
    
    def get_adj(self):
        return (
            [(self.point, direction) for direction in self.direction.get_neighboring()]
            + [(self.point.add_relative(0, 1, self.direction), self.direction)]
        )

class Router:
    def __init__(self, world_map:Map):
        self.world_map = world_map

    def find_route_to_intresting(initial_state:State) -> List[State]:
        pass