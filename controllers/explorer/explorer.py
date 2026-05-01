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
        self.robot = Robot([
            (('ps5', 1.0),),
            (('ps5', 0.5), ('ps6', 0.5)),
            (('ps6', 1.0),),
            (('ps7', 1.0),),
            (('ps7', 0.5), ('ps0', 0.5))
        ])
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

            for dx, dy, lower_threhold, upper_threshold, sensor_nums in (
                (1, -3, 70, 100, (0,)),
                (0, -3, 70, 100, (0, 7)),
                (-1, -3, 70, 100, (7,)),
                (1, -2, 200, 500, (0,)),
                (0, -2, 500, 1000, (0, 7)),
                (-1, -2, 200, 500, (7,)),
                (2, 0, 500, 1000, (2,)),
                (2, -1, 200, 500, (1, 2)),
                (2, -2, 200, 500, (1,)),
                (3, 0, 70, 100, (5,)),
                (3, -1, 70, 100, (5, 6)),
                (3, -2, 70, 100, (6,)),
                (-2, 0, 500, 1000, (5,)),
                (-2, -1, 200, 500, (5, 6)),
                (-2, -2, 200, 500, (6,)),
                (-3, 0, 70, 100, (2,)),
                (-3, -1, 70, 100, (1, 2)),
                (-3, -2, 70, 100, (1,))
            ):
                key_sensor_values = [sensor_values[i] for i in sensor_nums]
                mean_sensor_value = sum(key_sensor_values) / len(key_sensor_values)
                if point.add_relative(dx, dy):
                    pass
                


if __name__ == '__main__':
    controller = RobotController()
    controller.run()