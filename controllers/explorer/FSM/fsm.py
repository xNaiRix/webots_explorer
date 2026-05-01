from map import Direction, MapPoint, Map

class FSMHandler:
    def __init__(self, world_map:Map):
        self.world_map = world_map
    
    def tick(self, x:float, y:float, theta:float, point:MapPoint, direction:Direction):
        pass