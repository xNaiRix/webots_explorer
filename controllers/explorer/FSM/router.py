from typing import List, Tuple
from random import randint
from map import Direction, MapPoint, Map

class Node:
    def __init__(self, point:MapPoint, direction:Direction):
        self.point = point
        self.direction = direction

    def __hash__(self) -> int:
        return hash((self.point, self.direction))
    
    def __eq__(self, other:"Node") -> bool:
        return self.point == other.point and self.direction == other.direction

    def __ne__(self, other:"Node") -> bool:
        return not (self == other)
    
    def get_adj_with_weights(self) -> List[Tuple["Node", float]]:
        return (
            [(Node(self.point, direction), 5) for direction in self.direction.get_neighboring()]
            + [(Node(self.point.add_relative(0, 1, self.direction), self.direction), 1),
               (Node(self.point.add_relative(0, -1, self.direction), self.direction), 5)]
        )

class Router:
    def __init__(self, world_map:Map):
        self.world_map = world_map

    def best_route_to_intresting(self, first_node:Node) -> List[Node] | None:
        priority_queue = {0: [first_node]}
        used_nodes = {first_node: None}
        while priority_queue:
            lowest_value = min(priority_queue.keys())
            equal_priority_list = priority_queue[lowest_value]
            if len(equal_priority_list) > 1:
                node = equal_priority_list.pop(randint(0, len(equal_priority_list) - 1))
            else:
                node = priority_queue.pop(lowest_value)[0]
            if self.world_map.is_interesting(node.point, node.direction):
                break
            for next_node, extra_value in node.get_adj_with_weights():
                if self.world_map.robot_can_be_placed(next_node.point) and next_node not in used_nodes:
                    used_nodes[next_node] = node
                    priority_queue[lowest_value + extra_value] = priority_queue.get(lowest_value + extra_value, [])
                    priority_queue[lowest_value + extra_value].append(next_node)
        else:
            return None
        best_route = [node]
        while used_nodes[best_route[0]] is not None:
            best_route.insert(0, used_nodes[best_route[0]])
        return best_route
    
    def heuristic(start_node:Node, end_node:Node) -> int:
        value = abs(start_node.point.cell_x - end_node.point.cell_x) \
                + abs(start_node.point.cell_y - end_node.point.cell_y)
        if start_node.direction in end_node.direction.get_neighboring():
            value += 1
        elif start_node.direction != end_node.direction:
            value += 2
        return value
    
    