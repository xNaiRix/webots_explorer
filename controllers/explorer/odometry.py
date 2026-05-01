"""
Модуль одометрии с коррекцией IMU.
Использует энкодеры колес и гироскоп для точного отслеживания положения.
"""
import math


class Odometry:
    """
    Класс для отслеживания положения робота с использованием сенсорного fusion.
    
    Параметры робота e-puck:
    - wheel_radius: 0.0205 м
    - wheel_base: 0.052 м (расстояние между колесами)
    """
    
    def __init__(self, start_x=0.65, start_y=0.65, start_theta=0.0):
        """
        Инициализация одометрии.
        
        Args:
            start_x: Начальная координата X (м)
            start_y: Начальная координата Y (м)
            start_theta: Начальный угол (рад)
        """
        # Параметры робота
        self.WHEEL_RADIUS = 0.0205  # м
        self.WHEEL_BASE = 0.052     # м
        
        # Текущая поза
        self.x = start_x
        self.y = start_y
        self.theta = start_theta  # Ориентация (рад), 0 = смотрит вдоль оси X
        
        # Предыдущие значения энкодеров
        self.prev_left = 0.0
        self.prev_right = 0.0
        
        # Параметры фильтра
        self.alpha = 0.7  # Вес энкодеров в комплементарном фильтре (0-1)
        
        # Интегрированный угол от гироскопа
        self.gyro_theta = start_theta
        
        # Флаг инициализации
        self.initialized = False
        
        # Статистика
        self.distance_traveled = 0.0
        
    def update_from_encoders(self, left_pos, right_pos, dt):
        """
        Обновляет позу на основе энкодеров колес.
        
        Args:
            left_pos: Текущая позиция левого энкодера (рад)
            right_pos: Текущая позиция правого энкодера (рад)
            dt: Временной шаг (с)
            
        Returns:
            tuple: (delta_x, delta_y, delta_theta) изменения за шаг
        """
        if not self.initialized:
            self.prev_left = left_pos
            self.prev_right = right_pos
            self.initialized = True
            return 0.0, 0.0, 0.0
        
        # Вычисляем пройденное расстояние каждым колесом
        delta_left = (left_pos - self.prev_left) * self.WHEEL_RADIUS
        delta_right = (right_pos - self.prev_right) * self.WHEEL_RADIUS
        
        # Сохраняем для следующего шага
        self.prev_left = left_pos
        self.prev_right = right_pos
        
        # Линейное перемещение и поворот
        delta_distance = (delta_left + delta_right) / 2.0
        delta_theta = (delta_right - delta_left) / self.WHEEL_BASE
        
        # Обновляем пройденное расстояние
        self.distance_traveled += abs(delta_distance)
        
        # Вычисляем изменение позиции
        delta_x = delta_distance * math.cos(self.theta)
        delta_y = delta_distance * math.sin(self.theta)
        
        return delta_x, delta_y, delta_theta
    
    def update_from_gyro(self, gyro_z, dt):
        """
        Обновляет угол на основе гироскопа.
        
        Args:
            gyro_z: Угловая скорость по оси Z (рад/с)
            dt: Временной шаг (с)
            
        Returns:
            float: Изменение угла по гироскопу (рад)
        """
        delta_theta_gyro = gyro_z * dt
        self.gyro_theta += delta_theta_gyro
        return delta_theta_gyro
    
    def update(self, left_pos, right_pos, gyro_z, dt):
        """
        Основной метод обновления одометрии с сенсорным fusion.
        
        Args:
            left_pos: Позиция левого энкодера (рад)
            right_pos: Позиция правого энкодера (рад)
            gyro_z: Угловая скорость по оси Z (рад/с)
            dt: Временной шаг (с)
        """
        # Обновляем от энкодеров
        delta_x, delta_y, delta_theta_enc = self.update_from_encoders(
            left_pos, right_pos, dt
        )
        
        # Обновляем от гироскопа
        delta_theta_gyro = self.update_from_gyro(gyro_z, dt)
        
        # Комплементарный фильтр для угла
        # self.alpha - доверие к энкодерам, (1-self.alpha) - к гироскопу
        if abs(delta_theta_enc) < 0.5:  # Игнорируем большие скачки (возможно проскальзывание)
            filtered_delta_theta = (
                self.alpha * delta_theta_enc + (1 - self.alpha) * delta_theta_gyro
            )
        else:
            filtered_delta_theta = delta_theta_gyro  # При проскальзывании доверяем гироскопу
        
        # Обновляем позу
        self.theta += filtered_delta_theta
        # Нормализуем угол в диапазон [-π, π]
        self.theta = math.atan2(math.sin(self.theta), math.cos(self.theta))
        
        self.x += delta_x
        self.y += delta_y
        
    def get_pose(self):
        """
        Возвращает текущую позу робота.
        
        Returns:
            tuple: (x, y, theta) в метрах и радианах
        """
        return self.x, self.y, self.theta
    
    def set_pose(self, x, y, theta):
        """
        Устанавливает позу робота (например, при коррекции).
        
        Args:
            x: Координата X (м)
            y: Координата Y (м)
            theta: Угол (рад)
        """
        self.x = x
        self.y = y
        self.theta = theta
        self.gyro_theta = theta
    
    def distance_to(self, target_x, target_y):
        """
        Вычисляет евклидово расстояние до целевой точки.
        
        Args:
            target_x: Целевая координата X (м)
            target_y: Целевая координата Y (м)
            
        Returns:
            float: Расстояние в метрах
        """
        dx = target_x - self.x
        dy = target_y - self.y
        return math.sqrt(dx*dx + dy*dy)
    
    def angle_to(self, target_x, target_y):
        """
        Вычисляет угол от текущего положения до целевой точки.
        
        Args:
            target_x: Целевая координата X (м)
            target_y: Целевая координата Y (м)
            
        Returns:
            float: Угол в радианах относительно текущей ориентации
        """
        dx = target_x - self.x
        dy = target_y - self.y
        target_angle = math.atan2(dy, dx)
        
        # Разность углов
        angle_diff = target_angle - self.theta
        # Нормализуем в диапазон [-π, π]
        while angle_diff > math.pi:
            angle_diff -= 2 * math.pi
        while angle_diff < -math.pi:
            angle_diff += 2 * math.pi
            
        return angle_diff
    
    def get_stats(self):
        """
        Возвращает статистику одометрии.
        
        Returns:
            dict: Статистика (пройденное расстояние и т.д.)
        """
        return {
            'distance_traveled': self.distance_traveled,
            'x': self.x,
            'y': self.y,
            'theta': self.theta,
            'theta_deg': math.degrees(self.theta)
        }