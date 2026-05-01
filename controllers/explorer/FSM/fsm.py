from map import Direction, MapPoint, Map
from forward_state import ForwardState
from turn_state import TurnState, TurnLeftState, TurnRightState

class FSMHandler:
    def __init__(self, world_map:Map):
        self.world_map = world_map
        self.plan = []
    
    def tick(self, x:float, y:float, theta:float, point:MapPoint, direction:Direction):
        if self.plan:
            current_state = self.plan[0]
            if current_state.is_finished(x, y, theta, point, direction):
                self.plan.pop(0)
        
        # BFS

        if self.plan:
            current_state = self.plan[0]
            return current_state.tick(x, y, theta, point, direction)
        
        return (0.0, 0.0)