from typing import List
from map import Direction, MapPoint, Map

class Node:
    def __init__(self, point:MapPoint, direction:Direction):
        self.point = point
        self.direction = direction

    def __hash__(self):
        return hash((self.point, self.direction))
    
    def __eq__(self, other):
        return self.point == other.point and self.direction == other.direction

    def __ne__(self, other):
        return not (self == other)
    
    def get_adj(self) -> List["Node"]:
        return (
            [Node(self.point, direction) for direction in self.direction.get_neighboring()]
            + [Node(self.point.add_relative(0, 1, self.direction), self.direction)]
        )

class Router:
    def __init__(self, world_map:Map):
        self.world_map = world_map

    def find_route_to_intresting(self, first_node:Node) -> List[Node] | None:
        used_nodes = {first_node: None}
        queue = [first_node]
        while queue:
            node = queue.pop(0)
            if self.world_map.is_interesting(node.point, node.direction):
                break
            for next_node in node.get_adj():
                if self.world_map.robot_can_be_placed(next_node.point) and next_node not in used_nodes:
                    used_nodes[next_node] = node
                    queue.append(next_node)
        else:
            return None
        route = [node]
        while used_nodes[route[0]] is not None:
            route.insert(0, used_nodes[route[0]])
        return route