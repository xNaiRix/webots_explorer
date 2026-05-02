from sys import exit
from typing import List, Tuple
from constants import MAX_COORD_ERROR, MAX_GET_OUT_ATTEMPTS
from map import Direction, MapPoint, Map
from FSM.state import State
from FSM.forward_state import ForwardState
from FSM.turn_state import TurnLeftState, shortest_turn_state
from FSM.router import Node, Router

class FSMHandler:
    def __init__(self, world_map:Map):
        self.world_map = world_map
        self.router = Router(self.world_map)
        self.plan: List[State] = []
        self.get_out_attempts = 0
    
    def tick(self, x:float, y:float, theta:float, point:MapPoint, direction:Direction) -> Tuple[float, float]:
        if self.plan:
            current_state = self.plan[0]
            if current_state.is_finished(x, y, theta, point, direction):
                self.plan.pop(0)

        if not self.plan:
            if point.distance_to_float_coords(x, y) >= MAX_COORD_ERROR:
                direction1, direction2 = direction.get_neighboring()
                route1 = self.router.best_route_to_intresting(Node(point, direction1))
                route2 = self.router.best_route_to_intresting(Node(point, direction2))
                if len(route1) < len(route2):
                    route = route1
                else:
                    route = route2
                route.insert(0, Node(point, direction))
                route.insert(2, route[1])
            else:
                route = self.router.best_route_to_intresting(Node(point, direction))
        
            if route is None:
                if self.get_out_attempts >= MAX_GET_OUT_ATTEMPTS:
                    return None
                self.get_out_attempts += 1
                self.plan = [
                    shortest_turn_state(self.world_map, direction, direction.get_opposite()),
                    ForwardState(self.world_map, point.add_relative(0, -1, direction))
                ]
            else:
                index = 0
                while index < len(route) - 1:
                    start_index = index
                    if route[index].direction == route[index + 1].direction:
                        while index < len(route) - 1 and route[index].direction == route[index + 1].direction:
                            index += 1
                        state = ForwardState(self.world_map, route[index].point)
                    else:
                        while index < len(route) - 1 and route[index].direction != route[index + 1].direction:
                            index += 1
                        state = shortest_turn_state(self.world_map,
                                                    route[start_index].direction,
                                                    route[index].direction)
                    self.plan.append(state)
                
                self.get_out_attempts = 0

        if self.plan:
            current_state = self.plan[0]
            return current_state.tick(x, y, theta, point, direction)
        
        return (0.0, 0.0)