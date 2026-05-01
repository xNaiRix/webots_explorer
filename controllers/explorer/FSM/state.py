from abc import ABC, abstractmethod
from typing import Tuple
from map import Direction, MapPoint, Map


class State(ABC):
    def __init__(self, world_map:Map):
        self.world_map = world_map

    @abstractmethod
    def tick(self, x:float, y:float, theta:float, point:MapPoint, direction:Direction) -> Tuple[float, float]:
        pass

    @abstractmethod
    def is_finished(self, x:float, y:float, theta:float, point:MapPoint, direction:Direction) -> bool:
        pass