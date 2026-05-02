import math
import heapq
import numpy as np
from map import Map

class AstarRunner:
    def __init__(self, world_map: Map):
        self.world_map = world_map
    
    @staticmethod
    def heuristic():
        pass

def distance(a, b):
    return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)

def heuristic(a, b):

    # Для алгоритма Дейкстры:
    # return 0
    
    return distance(a, b)

def astar(grid, start, goal):
    rows, cols = len(grid), len(grid[0])
    
    # Очередь с приоритетом: (f_score, позиция)
    open_set = [(0, start)]
    came_from = {}
    g_score = {start: 0}
    
    # 8 направлений: вверх, вниз, влево, вправо + диагонали
    directions = [
        (0, 1), (0, -1), (1, 0), (-1, 0),
        (1, 1), (1, -1), (-1, 1), (-1, -1)
    ]
    
    visited = set()
    
    while open_set:
        _, current = heapq.heappop(open_set)
        
        if current in visited:
            continue
        visited.add(current)
        
        # Цель достигнута!
        if current == goal:
            # Восстанавливаем путь
            path = [current]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            return path[::-1], visited
        
        # Проверяем соседей
        for dx, dy in directions:
            nx, ny = current[0] + dx, current[1] + dy
            neighbor = (nx, ny)
            
            # Проверка границ и препятствий
            if (0 <= nx < rows and 0 <= ny < cols 
                and grid[nx][ny] == 0 
                and neighbor not in visited
                and (dx*dx + dy*dy == 1 or (grid[nx][current[1]] == 0 and grid[current[0]][ny] == 0))
                ):
                
                # Стоимость: 1.0 для прямых, ~1.41 для диагональных
                cost = math.sqrt(dx*dx + dy*dy)
                tentative_g = g_score[current] + cost
                
                if tentative_g < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f = tentative_g + heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f, neighbor))
    
    return None, visited  # Путь не найден