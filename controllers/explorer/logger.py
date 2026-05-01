from pathlib import Path
import csv, math

class Logger:
    def __init__(self):
        self.base_dir = Path("../../statistics/data")
        self.trajectory_path =  self.base_dir / "trajectory.csv"
        self.sensors_path = self.base_dir / "sensors.csv"
        with open(self.trajectory_path, "w", newline='') as f:
            w = csv.writer(f)
            w.writerow(['time', 'x', 'y', 'theta'])
        with open(self.sensors_path, "w", newline='') as f:
            w = csv.writer(f)
            w.writerow(['time'] + [f'sensor_{i}' for i in range(8)])
        

    def _write_row(self, path, values):
        """Внутренний метод для записи строки"""
        with open(path, 'a', newline='') as f:
            csv.writer(f).writerow(values)

    def log_odometry(self, x, y, theta, timestamp):
        self._write_row(self.trajectory_path, [timestamp, x, y, theta])
    def log_sensors(self, sensor_values, timestamp):
        self._write_row(self.sensors_path, [timestamp] + sensor_values)