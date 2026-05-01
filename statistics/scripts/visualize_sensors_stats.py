"""
Скрипт для визуализации статистики по датчикам расстояния робота.
Анализирует данные из sensors.csv и генерирует графики и статистический отчёт.
"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

def load_sensor_data(sensors_path=None):
    """
    Загружает данные датчиков из CSV файла.
    
    Args:
        sensors_path: Путь к CSV файлу с данными датчиков
    
    Returns:
        DataFrame с данными или None в случае ошибки
    """
    if sensors_path is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        sensors_path = os.path.join(script_dir, '..', 'data', 'sensors.csv')
        sensors_path = os.path.normpath(sensors_path)
    
    if not os.path.exists(sensors_path):
        print(f"Файл {sensors_path} не найден.")
        return None
    
    try:
        df = pd.read_csv(sensors_path)
        if df.empty:
            print("Файл sensors.csv пуст.")
            return None
        
        # Переименуем колонки для удобства
        if 'timestamp' not in df.columns and 'time' in df.columns:
            df = df.rename(columns={'time': 'timestamp'})
        
        print(f"Загружено {len(df)} записей датчиков")
        return df
    except Exception as e:
        print(f"Ошибка чтения CSV датчиков: {e}")
        return None

def calculate_sensor_statistics(df):
    """
    Вычисляет статистику для каждого датчика.
    
    Args:
        df: DataFrame с данными датчиков
    
    Returns:
        DataFrame со статистикой
    """
    sensor_cols = [col for col in df.columns if col.startswith('sensor_')]
    
    if not sensor_cols:
        print("Не найдены колонки с данными датчиков.")
        return None
    
    stats_list = []
    for col in sensor_cols:
        if col in df.columns:
            values = df[col]
            stats_dict = {
                'Датчик': col,
                'Минимум': values.min(),
                'Максимум': values.max(),
                'Среднее': values.mean(),
                'Медиана': values.median(),
                'Стандартное отклонение': values.std(),
                'Дисперсия': values.var(),
                'Квантиль 25%': values.quantile(0.25),
                'Квантиль 75%': values.quantile(0.75),
                'Количество измерений': len(values),
                'Количество пропусков': values.isna().sum()
            }
            stats_list.append(stats_dict)
    
    stats_df = pd.DataFrame(stats_list)
    return stats_df

def visualize_sensor_time_series(df, output_path=None):
    """
    Создает графики временных рядов для каждого датчика.
    
    Args:
        df: DataFrame с данными датчиков
        output_path: Путь для сохранения графика
    """
    if output_path is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(script_dir, '..', 'visualisation', 'sensors_time_series.png')
        output_path = os.path.normpath(output_path)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    sensor_cols = [col for col in df.columns if col.startswith('sensor_')]
    n_sensors = len(sensor_cols)
    
    if n_sensors == 0:
        print("Нет данных датчиков для визуализации.")
        return
    
    # Определяем размер сетки графиков
    n_cols = 2
    n_rows = (n_sensors + 1) // 2
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(14, 4 * n_rows))
    axes = axes.flatten() if n_sensors > 1 else [axes]
    
    for idx, col in enumerate(sensor_cols):
        if idx >= len(axes):
            break
            
        ax = axes[idx]
        ax.plot(df['timestamp'], df[col], 'b-', linewidth=1.5, alpha=0.7)
        ax.set_xlabel('Время (с)')
        ax.set_ylabel('Значение датчика')
        ax.set_title(f'{col} - временной ряд')
        ax.grid(True, alpha=0.3)
        
        # Добавляем горизонтальную линию для среднего значения
        mean_val = df[col].mean()
        ax.axhline(y=mean_val, color='r', linestyle='--', alpha=0.5, 
                  label=f'Среднее: {mean_val:.2f}')
        ax.legend(fontsize='small')
    
    # Скрываем пустые оси
    for idx in range(len(sensor_cols), len(axes)):
        axes[idx].set_visible(False)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    print(f"График временных рядов сохранен как {output_path}")
    plt.close()

def visualize_sensor_distributions(df, output_path=None):
    """
    Создает гистограммы распределения значений для каждого датчика.
    
    Args:
        df: DataFrame с данными датчиков
        output_path: Путь для сохранения графика
    """
    if output_path is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(script_dir, '..', 'visualisation', 'sensors_distributions.png')
        output_path = os.path.normpath(output_path)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    sensor_cols = [col for col in df.columns if col.startswith('sensor_')]
    n_sensors = len(sensor_cols)
    
    if n_sensors == 0:
        print("Нет данных датчиков для визуализации.")
        return
    
    # Определяем размер сетки графиков
    n_cols = 2
    n_rows = (n_sensors + 1) // 2
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(14, 4 * n_rows))
    axes = axes.flatten() if n_sensors > 1 else [axes]
    
    for idx, col in enumerate(sensor_cols):
        if idx >= len(axes):
            break
            
        ax = axes[idx]
        values = df[col].dropna()
        
        # Гистограмма с кривой плотности
        ax.hist(values, bins=30, density=True, alpha=0.6, color='g', 
               edgecolor='black', linewidth=0.5)
        
        # Кривая плотности
        from scipy.stats import gaussian_kde
        if len(values) > 1:
            kde = gaussian_kde(values)
            x_range = np.linspace(values.min(), values.max(), 100)
            ax.plot(x_range, kde(x_range), 'r-', linewidth=2)
        
        ax.set_xlabel('Значение датчика')
        ax.set_ylabel('Плотность')
        ax.set_title(f'{col} - распределение')
        ax.grid(True, alpha=0.3)
        
        # Добавляем статистику на график
        stats_text = f'Среднее: {values.mean():.2f}\nСтд: {values.std():.2f}'
        ax.text(0.05, 0.95, stats_text, transform=ax.transAxes, 
               fontsize=10, verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    # Скрываем пустые оси
    for idx in range(len(sensor_cols), len(axes)):
        axes[idx].set_visible(False)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    print(f"График распределений сохранен как {output_path}")
    plt.close()

def visualize_sensor_correlation(df, output_path=None):
    """
    Создает тепловую карту корреляций между датчиками.
    
    Args:
        df: DataFrame с данными датчиков
        output_path: Путь для сохранения графика
    """
    if output_path is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(script_dir, '..', 'visualisation', 'sensors_correlation.png')
        output_path = os.path.normpath(output_path)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    sensor_cols = [col for col in df.columns if col.startswith('sensor_')]
    
    if len(sensor_cols) < 2:
        print("Недостаточно датчиков для анализа корреляции.")
        return
    
    # Вычисляем матрицу корреляций
    corr_matrix = df[sensor_cols].corr()
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Тепловая карта
    im = ax.imshow(corr_matrix, cmap='coolwarm', vmin=-1, vmax=1)
    
    # Добавляем значения в ячейки
    for i in range(len(sensor_cols)):
        for j in range(len(sensor_cols)):
            text = ax.text(j, i, f'{corr_matrix.iloc[i, j]:.2f}',
                          ha="center", va="center", color="black", fontsize=9)
    
    # Настройки осей
    ax.set_xticks(np.arange(len(sensor_cols)))
    ax.set_yticks(np.arange(len(sensor_cols)))
    ax.set_xticklabels(sensor_cols, rotation=45, ha='right')
    ax.set_yticklabels(sensor_cols)
    
    ax.set_title('Корреляция между датчиками')
    plt.colorbar(im, ax=ax)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    print(f"График корреляций сохранен как {output_path}")
    plt.close()

def visualize_sensor_boxplots(df, output_path=None):
    """
    Создает boxplot для сравнения распределений датчиков.
    
    Args:
        df: DataFrame с данными датчиков
        output_path: Путь для сохранения графика
    """
    if output_path is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(script_dir, '..', 'visualisation', 'sensors_boxplots.png')
        output_path = os.path.normpath(output_path)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    sensor_cols = [col for col in df.columns if col.startswith('sensor_')]
    
    if len(sensor_cols) == 0:
        print("Нет данных датчиков для визуализации.")
        return
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Подготовка данных для boxplot
    data = [df[col].dropna() for col in sensor_cols]
    
    # Создаем boxplot
    bp = ax.boxplot(data, labels=sensor_cols, patch_artist=True)
    
    # Настраиваем цвета
    colors = plt.cm.Set3(np.linspace(0, 1, len(sensor_cols)))
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
    
    ax.set_xlabel('Датчики')
    ax.set_ylabel('Значение датчика')
    ax.set_title('Boxplot распределений значений датчиков')
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    print(f"График boxplot сохранен как {output_path}")
    plt.close()

def generate_sensor_report(df, stats_df, output_path=None):
    """
    Генерирует текстовый отчет со статистикой датчиков.
    
    Args:
        df: DataFrame с данными датчиков
        stats_df: DataFrame со статистикой
        output_path: Путь для сохранения отчета
    """
    if output_path is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(script_dir, '..', 'visualisation', 'sensors_report.txt')
        output_path = os.path.normpath(output_path)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    sensor_cols = [col for col in df.columns if col.startswith('sensor_')]
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("ОТЧЕТ ПО СТАТИСТИКЕ ДАТЧИКОВ РОБОТА\n")
        f.write("=" * 60 + "\n\n")
        
        f.write(f"Общая информация:\n")
        f.write(f"  Всего записей: {len(df)}\n")
        f.write(f"  Временной диапазон: {df['timestamp'].min():.2f} - {df['timestamp'].max():.2f} с\n")
        f.write(f"  Длительность: {df['timestamp'].max() - df['timestamp'].min():.2f} с\n")
        f.write(f"  Количество датчиков: {len(sensor_cols)}\n\n")
        
        f.write("Статистика по датчикам:\n")
        f.write("-" * 60 + "\n")
        
        if stats_df is not None:
            # Записываем статистику в удобном формате
            for _, row in stats_df.iterrows():
                f.write(f"\n{row['Датчик']}:\n")
                f.write(f"  Минимум: {row['Минимум']:.4f}\n")
                f.write(f"  Максимум: {row['Максимум']:.4f}\n")
                f.write(f"  Среднее: {row['Среднее']:.4f}\n")
                f.write(f"  Медиана: {row['Медиана']:.4f}\n")
                f.write(f"  Стандартное отклонение: {row['Стандартное отклонение']:.4f}\n")
                f.write(f"  Дисперсия: {row['Дисперсия']:.4f}\n")
                f.write(f"  Квантиль 25%: {row['Квантиль 25%']:.4f}\n")
                f.write(f"  Квантиль 75%: {row['Квантиль 75%']:.4f}\n")
                f.write(f"  Измерений: {int(row['Количество измерений'])}\n")
        
        # Дополнительная статистика
        f.write("\n" + "=" * 60 + "\n")
        f.write("ДОПОЛНИТЕЛЬНЫЙ АНАЛИЗ:\n")
        f.write("=" * 60 + "\n\n")
        
        # Анализ выбросов
        f.write("Выбросы (по правилу 1.5*IQR):\n")
        for col in sensor_cols:
            if col in df.columns:
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)][col]
                f.write(f"  {col}: {len(outliers)} выбросов ({len(outliers)/len(df)*100:.1f}%)\n")
        
        # Анализ корреляций
        if len(sensor_cols) >= 2:
            f.write("\nКорреляции между датчиками:\n")
            corr_matrix = df[sensor_cols].corr()
            for i in range(len(sensor_cols)):
                for j in range(i+1, len(sensor_cols)):
                    corr = corr_matrix.iloc[i, j]
                    f.write(f"  {sensor_cols[i]} - {sensor_cols[j]}: {corr:.3f}\n")
        
        f.write("\n" + "=" * 60 + "\n")
        f.write("РЕКОМЕНДАЦИИ:\n")
        f.write("=" * 60 + "\n\n")
        
        # Простые рекомендации на основе статистики
        if stats_df is not None:
            for _, row in stats_df.iterrows():
                sensor = row['Датчик']
                std = row['Стандартное отклонение']
                mean = row['Среднее']
                
                f.write(f"{sensor}:\n")
                if std / mean > 0.3 and mean > 0:
                    f.write(f"  • Высокая изменчивость данных (относительное стд: {std/mean:.2f})\n")
                if row['Количество пропусков'] > 0:
                    f.write(f"  • Обнаружены пропуски: {row['Количество пропусков']} значений\n")
                if row['Максимум'] - row['Минимум'] < 0.1:
                    f.write(f"  • Маленький динамический диапазон\n")
                f.write("\n")
    
    print(f"Текстовый отчет сохранен как {output_path}")

def visualize_sensor_statistics(sensors_path=None):
    """
    Основная функция визуализации статистики датчиков.
    
    Args:
        sensors_path: Путь к CSV файлу с данными датчиков
    """
    print("Визуализация статистики датчиков робота")
    print("=" * 50)
    
    # Загружаем данные
    df = load_sensor_data(sensors_path)
    if df is None:
        print("Не удалось загрузить данные датчиков.")
        return
    
    # Вычисляем статистику
    stats_df = calculate_sensor_statistics(df)
    
    if stats_df is not None:
        print("\n" + "=" * 50)
        print("ОСНОВНАЯ СТАТИСТИКА:")
        print("=" * 50)
        print(stats_df.to_string(index=False))
    
    # Создаем визуализации
    visualize_sensor_time_series(df)
    visualize_sensor_distributions(df)
    visualize_sensor_correlation(df)
    visualize_sensor_boxplots(df)
    
    # Генерируем отчет
    generate_sensor_report(df, stats_df)
    
    print("\n" + "=" * 50)
    print("ВИЗУАЛИЗАЦИЯ ЗАВЕРШЕНА")
    print("=" * 50)
    print("Созданы следующие файлы:")
    print("  • sensors_time_series.png - временные ряды датчиков")
    print("  • sensors_distributions.png - распределения значений")
    print("  • sensors_correlation.png - корреляции между датчиками")
    print("  • sensors_boxplots.png - boxplot сравнение датчиков")
    print("  • sensors_report.txt - текстовый отчет со статистикой")
    print("\nВсе файлы сохранены в папке statistics/visualisation/")

if __name__ == "__main__":
    visualize_sensor_statistics()