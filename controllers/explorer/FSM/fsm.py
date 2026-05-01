from map import Direction, MapPoint, Map
from forward_state import ForwardState
from turn_state import TurnState, TurnLeftState, TurnRightState, shortest_turn_state
from router import Node, Router

class FSMHandler:
    def __init__(self, world_map:Map):
        self.world_map = world_map
        self.router = Router(self.world_map)
        self.plan = []
    
    def tick(self, x:float, y:float, theta:float, point:MapPoint, direction:Direction):
        if self.plan:
            current_state = self.plan[0]
            if current_state.is_finished(x, y, theta, point, direction):
                self.plan.pop(0)
        
        if not self.plan:
            route = self.router.find_route_to_intresting(Node(point, direction))
        
            if route is None:
                return None
            
            index = 0
            while index < len(route) - 1:
                start_index = index
                if route[index].direction == route[index + 1].direction:
                    while index < len(route) - 1 and route[index].direction == route[index + 1].direction:
                        index += 1
                    state = ForwardState(self.world_map, route[index - 1])
                else:
                    while index < len(route) - 1 and route[index].direction != route[index + 1].direction:
                        index += 1
                    state = shortest_turn_state(self.world_map,
                                                route[start_index].direction,
                                                route[index - 1].direction)
                self.plan.append(state)

        if self.plan:
            current_state = self.plan[0]
            return current_state.tick(x, y, theta, point, direction)
        
        return (0.0, 0.0)