"""
Скрипт для визуализации карты, построенной роботом-разведчиком.
Реконструирует карту на основе данных траектории (trajectory.csv) и датчиков (sensors.csv).
Использует ту же логику, что и контроллер explorer.py для определения стен и пустых пространств.
"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import math
from enum import Enum

# Константы из проекта
CELL_SIDE = 25  # мм
ROBOT_CELL_RADIUS = 1

class Direction(str, Enum):
    N = "NORTH"
    S = "SOUTH"
    E = "EAST"
    W = "WEST"
    
    @property
    def angle(self) -> float:
        return {
            Direction.N: math.pi/2,
            Direction.S: -math.pi/2,
            Direction.E: 0,
            Direction.W: math.pi
        }[self]
    
    @staticmethod
    def from_angle(theta: float) -> "Direction":
        direction = [
            Direction.E,
            Direction.N,
            Direction.W,
            Direction.S
        ]
        # Нормализуем угол
        normalized = theta % (2 * math.pi)
        if normalized > math.pi:
            normalized -= 2 * math.pi
        idx = round(normalized / (math.pi/2)) % 4
        return direction[idx]

class MapPoint:
    def __init__(self, cell_x, cell_y):
        self.cell_x = cell_x
        self.cell_y = cell_y
    
    def __hash__(self):
        return hash((self.cell_x, self.cell_y))
    
    def __eq__(self, other):
        return self.cell_x == other.cell_x and self.cell_y == other.cell_y
    
    @staticmethod
    def from_float_coords(x: float, y: float) -> "MapPoint":
        return MapPoint(round(x / CELL_SIDE), round(y / CELL_SIDE))
    
    def add_relative(self, dx: int, dy: int, direction: Direction) -> "MapPoint":
        new_point = MapPoint(self.cell_x, self.cell_y)
        match direction:
            case Direction.N:
                new_point.cell_x += dx
                new_point.cell_y += dy
            case Direction.E:
                new_point.cell_x += dy
                new_point.cell_y += -dx
            case Direction.W:
                new_point.cell_x += -dy
                new_point.cell_y += dx
            case Direction.S:
                new_point.cell_x += -dx
                new_point.cell_y += -dy
        return new_point

class ReconstructedMap:
    """Упрощенная реконструкция карты на основе данных датчиков."""
    def __init__(self, width=200, height=200):
        self.width = width
        self.height = height
        # 0 - неизвестно, 1 - пусто, 2 - стена
        self.grid = np.zeros((width, height), dtype=int)
        # Счетчики подтверждений для каждой клетки
        self.wall_counts = np.zeros((width, height), dtype=int)
        self.empty_counts = np.zeros((width, height), dtype=int)
    
    def set_wall(self, point: MapPoint):
        if 0 <= point.cell_x < self.width and 0 <= point.cell_y < self.height:
            self.wall_counts[point.cell_x, point.cell_y] += 1
            # Если есть больше подтверждений стены, чем пустоты, считаем стеной
            if self.wall_counts[point.cell_x, point.cell_y] > self.empty_counts[point.cell_x, point.cell_y]:
                self.grid[point.cell_x, point.cell_y] = 2
    
    def set_empty(self, point: MapPoint):
        if 0 <= point.cell_x < self.width and 0 <= point.cell_y < self.height:
            self.empty_counts[point.cell_x, point.cell_y] += 1
            # Если есть больше подтверждений пустоты, чем стены, считаем пустым
            if self.empty_counts[point.cell_x, point.cell_y] >= self.wall_counts[point.cell_x, point.cell_y]:
                self.grid[point.cell_x, point.cell_y] = 1
    
    def get_grid(self):
        return self.grid

def load_data(trajectory_path=None, sensors_path=None):
    """Загружает данные траектории и датчиков."""
    if trajectory_path is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        trajectory_path = os.path.join(script_dir, '..', 'data', 'trajectory.csv')
        trajectory_path = os.path.normpath(trajectory_path)
    
    if sensors_path is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        sensors_path = os.path.join(script_dir, '..', 'data', 'sensors.csv')
        sensors_path = os.path.normpath(sensors_path)
    
    if not os.path.exists(trajectory_path):
        print(f"Файл {trajectory_path} не найден.")
        return None, None
    
    try:
        df_traj = pd.read_csv(trajectory_path)
        if 'timestamp' not in df_traj.columns and 'time' in df_traj.columns:
            df_traj = df_traj.rename(columns={'time': 'timestamp'})
    except Exception as e:
        print(f"Ошибка чтения CSV траектории: {e}")
        return None, None
    
    df_sensors = None
    if os.path.exists(sensors_path):
        try:
            df_sensors = pd.read_csv(sensors_path)
            if 'timestamp' not in df_sensors.columns and 'time' in df_sensors.columns:
                df_sensors = df_sensors.rename(columns={'time': 'timestamp'})
        except Exception as e:
            print(f"Ошибка чтения CSV датчиков: {e}")
            df_sensors = None
    
    return df_traj, df_sensors

def reconstruct_map(df_traj, df_sensors):
    """
    Реконструирует карту на основе данных траектории и датчиков.
    Использует упрощенную логику определения стен.
    """
    print("Реконструкция карты...")
    
    # Создаем карту
    rmap = ReconstructedMap(width=200, height=200)
    
    # Если нет данных датчиков, возвращаем пустую карту
    if df_sensors is None or len(df_sensors) == 0:
        print("Нет данных датчиков для реконструкции карты.")
        return rmap
    
    # Объединяем данные по времени (приблизительно)
    # Упрощение: будем обрабатывать каждую запись траектории и находить ближайшие данные датчиков
    sensor_times = df_sensors['timestamp'].values
    sensor_values = df_sensors[[f'sensor_{i}' for i in range(8)]].values
    
    for idx, row in df_traj.iterrows():
        time = row['timestamp']
        x = row['x']
        y = row['y']
        theta = row['theta']
        
        # Находим ближайшие данные датчиков
        time_diff = np.abs(sensor_times - time)
        closest_idx = np.argmin(time_diff)
        if time_diff[closest_idx] > 0.1:  # Если разница больше 0.1 сек, пропускаем
            continue
        
        sensor_vals = sensor_values[closest_idx]
        point = MapPoint.from_float_coords(x, y)
        direction = Direction.from_angle(theta)
        
        # Упрощенная логика: если значение датчика выше порога, считаем что есть стена
        # Пороги эмпирические (подобно триггерам Шмидта в контроллере)
        thresholds = {
            'far': 70,
            'near': 200
        }
        
        # Обрабатываем датчики согласно их расположению на роботе
        # Датчики 0 и 7 - спереди (в зависимости от направления)
        # Датчики 1-2 - справа, 5-6 - слева
        # Это упрощение, реальная геометрия сложнее
        
        # Фронтальные датчики (0 и 7)
        for dx, dy, sensor_idx in [(1, -3, 0), (0, -3, 7)]:
            viewed_point = point.add_relative(dx, dy, direction)
            if sensor_vals[sensor_idx] > thresholds['far']:
                rmap.set_wall(viewed_point)
            else:
                rmap.set_empty(viewed_point)
        
        # Боковые датчики (справа: 1, 2)
        for dx, dy, sensor_idx in [(3, -2, 1), (3, -1, 2)]:
            viewed_point = point.add_relative(dx, dy, direction)
            if sensor_vals[sensor_idx] > thresholds['far']:
                rmap.set_wall(viewed_point)
            else:
                rmap.set_empty(viewed_point)
        
        # Боковые датчики (слева: 5, 6)
        for dx, dy, sensor_idx in [(-3, -2, 6), (-3, -1, 5)]:
            viewed_point = point.add_relative(dx, dy, direction)
            if sensor_vals[sensor_idx] > thresholds['far']:
                rmap.set_wall(viewed_point)
            else:
                rmap.set_empty(viewed_point)
    
    print(f"Реконструировано: стен - {np.sum(rmap.grid == 2)}, пустых - {np.sum(rmap.grid == 1)}, неизвестно - {np.sum(rmap.grid == 0)}")
    return rmap

def visualize_map(rmap, trajectory_df=None, output_path=None):
    """
    Визуализирует реконструированную карту.
    
    Args:
        rmap: ReconstructedMap объект
        trajectory_df: DataFrame с траекторией для отображения пути
        output_path: Путь для сохранения графика
    """
    if output_path is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(script_dir, '..', 'visualisation', 'reconstructed_map.png')
        output_path = os.path.normpath(output_path)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    grid = rmap.get_grid()
    
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # Создаем цветовую карту: неизвестно - серый, пусто - белый, стена - черный
    cmap = plt.cm.colors.ListedColormap(['lightgray', 'white', 'black'])
    bounds = [-0.5, 0.5, 1.5, 2.5]
    norm = plt.cm.colors.BoundaryNorm(bounds, cmap.N)
    
    # Отображаем карту (транспонируем для правильной ориентации)
    im = ax.imshow(grid.T, cmap=cmap, norm=norm, origin='lower', 
                   extent=[0, grid.shape[0], 0, grid.shape[1]])
    
    # Добавляем траекторию, если предоставлена
    if trajectory_df is not None and len(trajectory_df) > 0:
        # Конвертируем координаты в клетки
        traj_cells_x = trajectory_df['x'] / CELL_SIDE
        traj_cells_y = trajectory_df['y'] / CELL_SIDE
        
        ax.plot(traj_cells_x, traj_cells_y, 'b-', alpha=0.5, linewidth=1, label='Траектория')
        ax.scatter(traj_cells_x.iloc[0], traj_cells_y.iloc[0], 
                  c='green', s=100, marker='o', label='Старт')
        ax.scatter(traj_cells_x.iloc[-1], traj_cells_y.iloc[-1], 
                  c='red', s=100, marker='x', label='Финиш')
    
    # Настройки графика
    ax.set_xlabel('Клетка X')
    ax.set_ylabel('Клетка Y')
    ax.set_title('Реконструированная карта окружения')
    
    # Легенда для цветов карты
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='lightgray', edgecolor='black', label='Неизвестно'),
        Patch(facecolor='white', edgecolor='black', label='Пусто'),
        Patch(facecolor='black', edgecolor='black', label='Стена')
    ]
    if trajectory_df is not None:
        legend_elements.append(plt.Line2D([0], [0], color='blue', lw=2, label='Траектория'))
        legend_elements.append(plt.Line2D([0], [0], marker='o', color='w', 
                                         markerfacecolor='green', markersize=10, label='Старт'))
        legend_elements.append(plt.Line2D([0], [0], marker='x', color='w', 
                                         markerfacecolor='red', markersize=10, label='Финиш'))
    
    ax.legend(handles=legend_elements, loc='upper right', fontsize='small')
    ax.grid(True, alpha=0.3, which='both', color='gray', linestyle='-', linewidth=0.5)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    print(f"Визуализация карты сохранена как {output_path}")
    plt.close()

def visualize_map_statistics(rmap, output_path=None):
    """
    Создает дополнительные графики со статистикой карты.
    
    Args:
        rmap: ReconstructedMap объект
        output_path: Путь для сохранения графика
    """
    if output_path is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(script_dir, '..', 'visualisation', 'map_statistics.png')
        output_path = os.path.normpath(output_path)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    grid = rmap.get_grid()
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # 1. Распределение типов клеток
    ax = axes[0, 0]
    labels = ['Неизвестно', 'Пусто', 'Стена']
    counts = [np.sum(grid == 0), np.sum(grid == 1), np.sum(grid == 2)]
    colors = ['lightgray', 'lightgreen', 'lightcoral']
    
    ax.bar(labels, counts, color=colors, edgecolor='black')
    ax.set_title('Распределение типов клеток')
    ax.set_ylabel('Количество клеток')
    
    # Добавляем значения на столбцы
    for i, count in enumerate(counts):
        ax.text(i, count + max(counts)*0.01, str(count), 
               ha='center', va='bottom', fontweight='bold')
    
    # 2. Карта уверенности (количество измерений)
    ax = axes[0, 1]
    confidence = rmap.wall_counts + rmap.empty_counts
    im = ax.imshow(confidence.T, cmap='YlOrRd', origin='lower')
    ax.set_title('Карта уверенности (общее количество измерений)')
    ax.set_xlabel('Клетка X')
    ax.set_ylabel('Клетка Y')
    plt.colorbar(im, ax=ax, label='Количество измерений')
    
    # 3. Соотношение стен/пустот
    ax = axes[1, 0]
    ratio = np.zeros_like(confidence, dtype=float)
    mask = confidence > 0
    ratio[mask] = rmap.wall_counts[mask] / confidence[mask]
    
    im = ax.imshow(ratio.T, cmap='RdBu', vmin=0, vmax=1, origin='lower')
    ax.set_title('Соотношение стен/пустот (0=все пусто, 1=все стены)')
    ax.set_xlabel('Клетка X')
    ax.set_ylabel('Клетка Y')
    plt.colorbar(im, ax=ax, label='Доля стен')
    
    # 4. Гистограмма уверенности
    ax = axes[1, 1]
    confidence_flat = confidence.flatten()
    confidence_flat = confidence_flat[confidence_flat > 0]  # Только измеренные клетки
    
    if len(confidence_flat) > 0:
        ax.hist(confidence_flat, bins=30, edgecolor='black', alpha=0.7)
        ax.set_title('Распределение количества измерений по клеткам')
        ax.set_xlabel('Количество измерений')
        ax.set_ylabel('Частота')
        ax.grid(True, alpha=0.3)
    else:
        ax.text(0.5, 0.5, 'Нет данных измерений', 
               ha='center', va='center', transform=ax.transAxes, fontsize=12)
        ax.set_title('Распределение количества измерений')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    print(f"Статистика карты сохранена как {output_path}")
    plt.close()

def generate_map_report(rmap, trajectory_df, output_path=None):
    """
    Генерирует текстовый отчет о реконструированной карте.
    
    Args:
        rmap: ReconstructedMap объект
        trajectory_df: DataFrame с траекторией
        output_path: Путь для сохранения отчета
    """
    if output_path is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(script_dir, '..', 'visualisation', 'map_report.txt')
        output_path = os.path.normpath(output_path)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    grid = rmap.get_grid()
    total_cells = grid.size
    unknown_cells = np.sum(grid == 0)
    empty_cells = np.sum(grid == 1)
    wall_cells = np.sum(grid == 2)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("ОТЧЕТ ПО РЕКОНСТРУИРОВАННОЙ КАРТЕ\n")
        f.write("=" * 60 + "\n\n")
        
        f.write("ОБЩАЯ СТАТИСТИКА:\n")
        f.write("-" * 40 + "\n")
        f.write(f"Всего клеток: {total_cells}\n")
        f.write(f"Неизвестные клетки: {unknown_cells} ({unknown_cells/total_cells*100:.1f}%)\n")
        f.write(f"Пустые клетки: {empty_cells} ({empty_cells/total_cells*100:.1f}%)\n")
        f.write(f"Клетки со стенами: {wall_cells} ({wall_cells/total_cells*100:.1f}%)\n\n")
        
        f.write("ИССЛЕДОВАННАЯ ОБЛАСТЬ:\n")
        f.write("-" * 40 + "\n")
        explored_cells = empty_cells + wall_cells
        f.write(f"Исследовано клеток: {explored_cells} ({explored_cells/total_cells*100:.1f}%)\n")
        
        # Вычисляем bounding box исследованной области
        explored_mask = (grid == 1) | (grid == 2)
        if np.any(explored_mask):
            x_indices, y_indices = np.where(explored_mask)
            min_x, max_x = x_indices.min(), x_indices.max()
            min_y, max_y = y_indices.min(), y_indices.max()
            f.write(f"Границы исследованной области:\n")
            f.write(f"  X: от {min_x} до {max_x} (ширина: {max_x - min_x + 1} клеток)\n")
            f.write(f"  Y: от {min_y} до {max_y} (высота: {max_y - min_y + 1} клеток)\n")
            f.write(f"  Площадь: {(max_x - min_x + 1) * (max_y - min_y + 1)} клеток\n")
        
        f.write("\nСТАТИСТИКА ИЗМЕРЕНИЙ:\n")
        f.write("-" * 40 + "\n")
        total_measurements = np.sum(rmap.wall_counts) + np.sum(rmap.empty_counts)
        f.write(f"Всего измерений: {total_measurements}\n")
        f.write(f"Измерений стен: {np.sum(rmap.wall_counts)}\n")
        f.write(f"Измерений пустот: {np.sum(rmap.empty_counts)}\n")
        
        # Средняя уверенность по клеткам
        measured_cells = np.sum((rmap.wall_counts + rmap.empty_counts) > 0)
        if measured_cells > 0:
            avg_confidence = total_measurements / measured_cells
            f.write(f"Среднее измерений на клетку: {avg_confidence:.1f}\n")
        
        if trajectory_df is not None and len(trajectory_df) > 0:
            f.write("\nСТАТИСТИКА ТРАЕКТОРИИ:\n")
            f.write("-" * 40 + "\n")
            f.write(f"Всего точек траектории: {len(trajectory_df)}\n")
            f.write(f"Временной диапазон: {trajectory_df['timestamp'].min():.1f} - {trajectory_df['timestamp'].max():.1f} с\n")
            f.write(f"Длительность: {trajectory_df['timestamp'].max() - trajectory_df['timestamp'].min():.1f} с\n")
            
            # Вычисляем покрытие карты траекторией
            traj_cells_x = (trajectory_df['x'] / CELL_SIDE).round().astype(int)
            traj_cells_y = (trajectory_df['y'] / CELL_SIDE).round().astype(int)
            unique_cells = set(zip(traj_cells_x, traj_cells_y))
            f.write(f"Уникальных посещенных клеток: {len(unique_cells)}\n")
        
        f.write("\n" + "=" * 60 + "\n")
        f.write("РЕКОМЕНДАЦИИ:\n")
        f.write("=" * 60 + "\n\n")
        
        if unknown_cells / total_cells > 0.7:
            f.write("• Большая часть карты неизвестна. Роботу нужно больше исследовать.\n")
        if wall_cells > 0 and empty_cells > 0:
            f.write(f"• Соотношение стен/пустот: {wall_cells/empty_cells:.2f}\n")
        if measured_cells < total_cells * 0.3:
            f.write("• Недостаточно измерений для уверенной реконструкции карты.\n")
        
        f.write("\n" + "=" * 60 + "\n")
    
    print(f"Отчет по карте сохранен как {output_path}")

def main():
    """Основная функция визуализации карты."""
    print("Визуализация реконструированной карты робота-разведчика")
    print("=" * 60)
    
    # Загружаем данные
    df_traj, df_sensors = load_data()
    
    if df_traj is None:
        print("Не удалось загрузить данные траектории.")
        return
    
    # Реконструируем карту
    rmap = reconstruct_map(df_traj, df_sensors)
    
    # Визуализируем карту
    visualize_map(rmap, df_traj)
    
    # Создаем дополнительные графики статистики
    visualize_map_statistics(rmap)
    
    # Генерируем отчет
    generate_map_report(rmap, df_traj)
    
    print("\n" + "=" * 60)
    print("ВИЗУАЛИЗАЦИЯ КАРТЫ ЗАВЕРШЕНА")
    print("=" * 60)
    print("Созданы следующие файлы:")
    print("  • reconstructed_map.png - реконструированная карта с траекторией")
    print("  • map_statistics.png - статистика карты")
    print("  • map_report.txt - текстовый отчет")
    print("\nВсе файлы сохранены в папке statistics/visualisation/")

if __name__ == "__main__":
    main()