"""
Главный контроллер робота-разведчика.
Интегрирует все модули: датчики, одометрию, навигацию и FSM.
"""
from robot.robot import Robot
import sys
import os
import csv
import time
from constants import CELL_SIDE

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from robot import Robot
from odometry import Odometry
from FSM.fsm import FSMHandler
from map import MapPoint, Map

class RobotController:
    def __init__(self):
        self.robot = Robot()
        self.odometry = Odometry()
        self.map = Map(self.robot)
        self.fsm = FSMHandler(self.robot, self.map)
        self.dt = self.robot.basic_time_step / 1000.0

    def run(self):
        while True:
            sensor_values = [sensor_ps.get_value() for sensor_ps in self.robot.sensors_ps]
            left_enc_pos = self.robot.left_encoder.get_value()
            right_enc_pos = self.robot.right_encoder.get_value()

            self.odometry.update(left_enc_pos, right_enc_pos, self.dt)
            x, y, theta = self.odometry.position
            point = MapPoint.from_float_coords(x, y, theta)

            for dx, dy, lower_threhold, upper_threshold in (
                (-1, 3, 70, 100),
                (0, 3, 70, 100),
                (1, 3, 70, 100),
                (-1, 2, 200, 500),
                (0, 2, 500, 1000),
                (1, 2, 200, 500),
                (-2, 0, 500, 1000),
                (-2, 1, 200, 500),
                (-2, 2, 200, 500),
                (2, 0, 500, 1000),
                (2, 1, 200, 500),
                (2, 2, 200, 500),
            ):
                pass
                


if __name__ == '__main__':
    controller = RobotController()
    controller.run()