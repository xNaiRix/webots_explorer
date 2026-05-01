"""
Скрипт для визуализации траектории робота из trajectory.csv и sensors.csv.
Генерирует график trajectory.png.
"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os


def visualize_trajectory(csv_path=None, sensors_path=None, output_path=None):
    """
    Визуализирует траекторию робота и данные датчиков.
    
    Args:
        csv_path: Путь к CSV файлу с траекторией
        sensors_path: Путь к CSV файлу с данными датчиков
        output_path: Путь для сохранения графика
    """
    # Устанавливаем пути по умолчанию относительно расположения скрипта
    if csv_path is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(script_dir, '..', 'data', 'trajectory.csv')
        csv_path = os.path.normpath(csv_path)
    
    if sensors_path is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        sensors_path = os.path.join(script_dir, '..', 'data', 'sensors.csv')
        sensors_path = os.path.normpath(sensors_path)
    
    if output_path is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(script_dir, '..', 'visualisation', 'trajectory.png')
        output_path = os.path.normpath(output_path)
    
    # Создаем папку для графиков, если её нет
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    if not os.path.exists(csv_path):
        print(f"Файл {csv_path} не найден. Запустите контроллер сначала.")
        return
    
    # Чтение данных траектории
    try:
        df_traj = pd.read_csv(csv_path)
    except Exception as e:
        print(f"Ошибка чтения CSV траектории: {e}")
        return
    
    # Чтение данных датчиков
    df_sensors = None
    if os.path.exists(sensors_path):
        try:
            df_sensors = pd.read_csv(sensors_path)
        except Exception as e:
            print(f"Ошибка чтения CSV датчиков: {e}")
            df_sensors = None
    
    print(f"Загружено {len(df_traj)} точек траектории")
    if df_sensors is not None:
        print(f"Загружено {len(df_sensors)} точек данных датчиков")
    
    if len(df_traj) == 0:
        print("Файл траектории пуст. Запустите контроллер сначала.")
        return
    
    # Переименуем колонки для удобства (если нужно)
    if 'timestamp' not in df_traj.columns and 'time' in df_traj.columns:
        df_traj = df_traj.rename(columns={'time': 'timestamp'})
    
    print(f"Диапазон времени: {df_traj['timestamp'].min():.1f} - {df_traj['timestamp'].max():.1f} с")
    
    # Создание графика - теперь 3x2 для большего количества информации
    fig, axes = plt.subplots(3, 2, figsize=(14, 12))
    
    # 1. Траектория в XY
    ax = axes[0, 0]
    ax.plot(df_traj['x'], df_traj['y'], 'b-', alpha=0.7, linewidth=1.5, label='Траектория')
    ax.scatter(df_traj['x'].iloc[0], df_traj['y'].iloc[0], c='green', s=100, marker='o', label='Старт')
    ax.scatter(df_traj['x'].iloc[-1], df_traj['y'].iloc[-1], c='red', s=100, marker='x', label='Финиш')
    ax.set_xlabel('X (мм)')
    ax.set_ylabel('Y (мм)')
    ax.set_title('Траектория робота в плоскости XY')
    ax.grid(True, alpha=0.3)
    ax.legend()
    ax.axis('equal')
    
    # 2. Позиция по времени
    ax = axes[0, 1]
    ax.plot(df_traj['timestamp'], df_traj['x'], 'b-', label='X позиция')
    ax.plot(df_traj['timestamp'], df_traj['y'], 'r-', label='Y позиция')
    ax.set_xlabel('Время (с)')
    ax.set_ylabel('Позиция (мм)')
    ax.set_title('Позиция робота по времени')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 3. Ориентация (theta) по времени
    ax = axes[1, 0]
    # Конвертируем радианы в градусы для лучшей читаемости
    theta_deg = np.degrees(df_traj['theta'])
    ax.plot(df_traj['timestamp'], theta_deg, 'g-', linewidth=1.5)
    ax.set_xlabel('Время (с)')
    ax.set_ylabel('Ориентация (градусы)')
    ax.set_title('Ориентация робота (θ) по времени')
    ax.grid(True, alpha=0.3)
    
    # 4. Данные датчиков (если доступны)
    ax = axes[1, 1]
    if df_sensors is not None and len(df_sensors) > 0:
        sensor_cols = [col for col in df_sensors.columns if col.startswith('sensor_')]
        if sensor_cols:
            # Показываем среднее значение датчиков
            if 'timestamp' not in df_sensors.columns and 'time' in df_sensors.columns:
                df_sensors = df_sensors.rename(columns={'time': 'timestamp'})
            
            # Интерполируем данные датчиков для совпадения с временем траектории
            for i, col in enumerate(sensor_cols[:4]):  # Показываем только первые 4 датчика
                ax.plot(df_sensors['timestamp'], df_sensors[col], 
                       alpha=0.7, linewidth=1, label=f'Датчик {i}')
            
            ax.set_xlabel('Время (с)')
            ax.set_ylabel('Значение датчика')
            ax.set_title('Данные датчиков расстояния (первые 4)')
            ax.legend(fontsize='small')
        else:
            ax.text(0.5, 0.5, 'Нет данных датчиков', 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=12)
            ax.set_title('Данные датчиков')
    else:
        ax.text(0.5, 0.5, 'Файл sensors.csv не найден или пуст', 
               horizontalalignment='center', verticalalignment='center',
               transform=ax.transAxes, fontsize=12)
        ax.set_title('Данные датчиков')
    ax.grid(True, alpha=0.3)
    
    # 5. Скорость движения (производная от позиции)
    ax = axes[2, 0]
    if len(df_traj) > 1:
        # Вычисляем скорость как производную от расстояния
        dt = np.diff(df_traj['timestamp'])
        dx = np.diff(df_traj['x'])
        dy = np.diff(df_traj['y'])
        distance = np.sqrt(dx**2 + dy**2)
        speed = distance / dt
        speed_time = df_traj['timestamp'].iloc[:-1] + dt/2  # Время в середине интервала
        
        ax.plot(speed_time, speed, 'purple', linewidth=1.5)
        ax.set_xlabel('Время (с)')
        ax.set_ylabel('Скорость (мм/с)')
        ax.set_title('Скорость движения робота')
        ax.grid(True, alpha=0.3)
    else:
        ax.text(0.5, 0.5, 'Недостаточно данных для расчета скорости', 
               horizontalalignment='center', verticalalignment='center',
               transform=ax.transAxes, fontsize=12)
        ax.set_title('Скорость движения')
    
    # 6. Фазовый портрет (dx vs dy)
    ax = axes[2, 1]
    if len(df_traj) > 1:
        dx = np.diff(df_traj['x'])
        dy = np.diff(df_traj['y'])
        
        # Цветовая карта по времени
        time_norm = (speed_time - speed_time.min()) / (speed_time.max() - speed_time.min())
        scatter = ax.scatter(dx, dy, c=time_norm, cmap='viridis', alpha=0.6, s=20)
        
        ax.axhline(y=0, color='k', linestyle='-', alpha=0.3)
        ax.axvline(x=0, color='k', linestyle='-', alpha=0.3)
        ax.set_xlabel('ΔX (мм/шаг)')
        ax.set_ylabel('ΔY (мм/шаг)')
        ax.set_title('Фазовый портрет движения (ΔX vs ΔY)')
        ax.grid(True, alpha=0.3)
        ax.axis('equal')
        
        # Добавляем цветовую шкалу
        plt.colorbar(scatter, ax=ax, label='Нормализованное время')
    else:
        ax.text(0.5, 0.5, 'Недостаточно данных для фазового портрета', 
               horizontalalignment='center', verticalalignment='center',
               transform=ax.transAxes, fontsize=12)
        ax.set_title('Фазовый портрет движения')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    print(f"График сохранен как {output_path}")
    
    # Дополнительная статистика
    print("\n" + "="*50)
    print("СТАТИСТИКА ТРАЕКТОРИИ:")
    print("="*50)
    print(f"Начальная позиция: ({df_traj['x'].iloc[0]:.1f}, {df_traj['y'].iloc[0]:.1f}) мм")
    print(f"Конечная позиция: ({df_traj['x'].iloc[-1]:.1f}, {df_traj['y'].iloc[-1]:.1f}) мм")
    
    # Вычисляем пройденное расстояние
    if len(df_traj) > 1:
        dx = df_traj['x'].diff()
        dy = df_traj['y'].diff()
        distance = np.sqrt(dx**2 + dy**2).sum()
        print(f"Пройденное расстояние: {distance:.1f} мм ({distance/1000:.3f} м)")
        
        # Смещение от старта
        displacement = np.sqrt((df_traj['x'].iloc[-1] - df_traj['x'].iloc[0])**2 + 
                              (df_traj['y'].iloc[-1] - df_traj['y'].iloc[0])**2)
        print(f"Смещение от старта: {displacement:.1f} мм")
        
        # Эффективность пути (прямолинейность)
        if distance > 0:
            path_efficiency = displacement / distance * 100
            print(f"Эффективность пути: {path_efficiency:.1f}%")
    
    # Статистика по времени
    total_time = df_traj['timestamp'].iloc[-1] - df_traj['timestamp'].iloc[0]
    print(f"Общее время движения: {total_time:.1f} с")
    
    if len(df_traj) > 1:
        avg_speed = distance / total_time if total_time > 0 else 0
        print(f"Средняя скорость: {avg_speed:.1f} мм/с ({avg_speed/1000:.3f} м/с)")
    
    # Статистика по ориентации
    theta_range = np.degrees(df_traj['theta'].max() - df_traj['theta'].min())
    print(f"Диапазон изменения ориентации: {theta_range:.1f}°")
    
    # Статистика датчиков
    if df_sensors is not None and len(df_sensors) > 0:
        sensor_cols = [col for col in df_sensors.columns if col.startswith('sensor_')]
        if sensor_cols:
            print(f"\nСТАТИСТИКА ДАТЧИКОВ:")
            for col in sensor_cols:
                if col in df_sensors.columns:
                    val = df_sensors[col]
                    print(f"  {col}: мин={val.min():.1f}, макс={val.max():.1f}, средн={val.mean():.1f}")
    
    print("="*50)


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