import math
from constants import ROBOT_WHEEL_BASE, ROBOT_WHEEL_RADIUS


class Odometry:
    def __init__(self, start_x=0.0, start_y=0.0, start_theta=0.0):
        # Текущая поза
        self.x = start_x
        self.y = start_y
        self.theta = start_theta  # Ориентация (рад), 0 = смотрит вдоль оси X
        
        # Предыдущие значения энкодеров
        self.prev_left_pos = 0.0
        self.prev_right_pos = 0.0
        
    def update(self, left_enc_pos, right_pos, dt):
        # Вычисляем пройденное расстояние каждым колесом
        delta_left = (left_enc_pos - self.prev_enc_left) * ROBOT_WHEEL_RADIUS
        delta_right = (right_pos - self.prev_enc_right) * ROBOT_WHEEL_RADIUS
        
        # Сохраняем для следующего шага
        self.prev_left_pos = left_enc_pos
        self.prev_right_pos = right_pos
        
        # Линейное перемещение и поворот
        delta_distance = (delta_left + delta_right) / 2.0
        delta_theta = (delta_right - delta_left) / ROBOT_WHEEL_BASE
        
        # Обновляем пройденное расстояние
        self.distance_traveled += abs(delta_distance)
        
        # Вычисляем изменение позиции
        delta_x = delta_distance * math.cos(self.theta)
        delta_y = delta_distance * math.sin(self.theta)
    
    @property
    def position(self):
        return self.x, self.y, self.theta