from pathlib import Path
import csv, math

class Logger:
    def __init__(self):
        self.base_dir = Path("../../statistics/data")
        self.trajectory_path =  self.base_dir / "trajectory.csv"
    def log_odometry(self, x, y, theta):
        with open(self.trajectory_path, "a") as f:
            w = csv.writer(f)