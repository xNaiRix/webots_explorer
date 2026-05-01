from pathlib import Path
import csv, math

class Logger:
    def __init__(self):
        self.base_dir = Path("../../statistics/data")
        self.trajectory_path =  self.base_dir / "trajectory.csv"
        self.sensors_path = self.base_dir / "sensors.csv"
        with open(self.trajectory_path, "w", newline='') as f:
            w = csv.writer(f)
            w.writerow(['step','time', 'x', 'y', 'theta'])
        with open(self.sensors_path, "w", newline='') as f:
            w = csv.writer(f)
            w.writerow(['step', 'time'] + [f'sensor_{i}' for i in range(8)])
        

    def _write_row(self, path, values):
        """Внутренний метод для записи строки"""
        with open(path, 'a', newline='') as f:
            csv.writer(f).writerow(values)

    def log_odometry(self, step, timestamp, x, y, theta):
        self._write_row(self.trajectory_path, [step, timestamp, x, y, theta])
    def log_sensors(self, step, timestamp, sensor_values):
        self._write_row(self.sensors_path, [step, timestamp] + sensor_values)