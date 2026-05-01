"""
Скрипт для визуализации траектории робота из trajectory.csv.
Генерирует график trajectory.png.
"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os


def visualize_trajectory(csv_path=None, output_path=None):
    """
    Визуализирует траекторию робота.
    
    Args:
        csv_path: Путь к CSV файлу с траекторией
        output_path: Путь для сохранения графика
    """
    # Устанавливаем пути по умолчанию относительно расположения скрипта
    if csv_path is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(script_dir, '..', 'data', 'trajectory.csv')
        csv_path = os.path.normpath(csv_path)
    
    if output_path is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(script_dir, '..', 'visualisation', 'trajectory.png')
        output_path = os.path.normpath(output_path)
    
    # Создаем папку для графиков, если её нет
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    if not os.path.exists(csv_path):
        print(f"Файл {csv_path} не найден. Запустите контроллер сначала.")
        return
    
    # Чтение данных
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"Ошибка чтения CSV: {e}")
        return
    
    print(f"Загружено {len(df)} точек траектории")
    print(f"Диапазон времени: {df['timestamp'].min():.1f} - {df['timestamp'].max():.1f} с")
    
    # Создание графика
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # 1. Траектория в XY
    ax = axes[0, 0]
    ax.plot(df['x'], df['y'], 'b-', alpha=0.7, linewidth=1.5, label='Траектория')
    ax.scatter(df['x'].iloc[0], df['y'].iloc[0], c='green', s=100, marker='o', label='Старт')
    ax.scatter(df['x'].iloc[-1], df['y'].iloc[-1], c='red', s=100, marker='x', label='Финиш')
    ax.scatter(0.65, 0.65, c='purple', s=80, marker='s', label='Цель (0.65, 0.65)')
    ax.set_xlabel('X (м)')
    ax.set_ylabel('Y (м)')
    ax.set_title('Траектория робота в плоскости XY')
    ax.grid(True, alpha=0.3)
    ax.legend()
    ax.axis('equal')
    
    # 2. Состояния FSM по времени
    ax = axes[0, 1]
    # Создаем числовое представление состояний для графика
    states = df['state'].unique()
    state_to_num = {state: i for i, state in enumerate(states)}
    df['state_num'] = df['state'].map(state_to_num)
    
    ax.plot(df['timestamp'], df['state_num'], 'r-', linewidth=2)
    ax.set_yticks(range(len(states)))
    ax.set_yticklabels(states)
    ax.set_xlabel('Время (с)')
    ax.set_ylabel('Состояние')
    ax.set_title('Состояния FSM во времени')
    ax.grid(True, alpha=0.3)
    
    # 3. Скорости колес
    ax = axes[1, 0]
    ax.plot(df['timestamp'], df['left_vel'], 'b-', label='Левое колесо')
    ax.plot(df['timestamp'], df['right_vel'], 'r-', label='Правое колесо')
    ax.set_xlabel('Время (с)')
    ax.set_ylabel('Скорость (рад/с)')
    ax.set_title('Скорости колес')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 4. Обнаружение препятствий
    ax = axes[1, 1]
    ax.plot(df['timestamp'], df['obstacle_detected'], 'g-', linewidth=1)
    ax.fill_between(df['timestamp'], 0, df['obstacle_detected'], alpha=0.3, color='green')
    ax.set_xlabel('Время (с)')
    ax.set_ylabel('Обнаружено препятствие')
    ax.set_title('Обнаружение препятствий (1 = да, 0 = нет)')
    ax.grid(True, alpha=0.3)
    ax.set_ylim(-0.1, 1.5)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    print(f"График сохранен как {output_path}")
    
    # Дополнительная статистика
    print("\nСТАТИСТИКА ТРАЕКТОРИИ:")
    print(f"Начальная позиция: ({df['x'].iloc[0]:.3f}, {df['y'].iloc[0]:.3f})")
    print(f"Конечная позиция: ({df['x'].iloc[-1]:.3f}, {df['y'].iloc[-1]:.3f})")
    print(f"Смещение от цели: {np.sqrt((df['x'].iloc[-1]-0.65)**2 + (df['y'].iloc[-1]-0.65)**2):.3f} м")
    
    # Вычисляем пройденное расстояние (приблизительно)
    dx = df['x'].diff()
    dy = df['y'].diff()
    distance = np.sqrt(dx**2 + dy**2).sum()
    print(f"Пройденное расстояние: {distance:.2f} м")
    
    # Время в каждом состоянии
    print("\nВремя в состояниях:")
    for state in states:
        state_time = df[df['state'] == state]['timestamp']
        if len(state_time) > 1:
            duration = state_time.max() - state_time.min()
            print(f"  {state}: {duration:.1f} с")
    
    # Показываем график
    plt.show()


def read_mission_stats(stats_path=None):
    """Читает и выводит статистику миссии."""
    if stats_path is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        stats_path = os.path.join(script_dir, '..', 'data', 'mission_stats.txt')
        stats_path = os.path.normpath(stats_path)
    
    if os.path.exists(stats_path):
        print("\n" + "="*50)
        print("СТАТИСТИКА МИССИИ:")
        print("="*50)
        with open(stats_path, 'r') as f:
            print(f.read())
        print("="*50)


if __name__ == "__main__":
    print("Визуализация траектории робота-разведчика")
    print("="*50)
    
    # Визуализируем траекторию
    visualize_trajectory()
    
    # Показываем статистику
    read_mission_stats()
    
    print("\nВизуализация завершена.")