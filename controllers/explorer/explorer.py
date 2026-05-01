"""
Главный контроллер робота-разведчика.
Интегрирует все модули: датчики, одометрию, навигацию и FSM.
"""
from robot.robot import Robot
import sys
import os
import csv
import time

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from robot import Robot
from odometry import Odometry
from FSM.fsm import FSMHandler
from map import Map

class RobotController:
    def __init__(self):
        self.robot = Robot()
        self.odometry = Odometry()
        self.map = Map(self.robot)
        self.fsm = FSMHandler(self.robot, self.map)
        self.dt = self.robot.basic_time_step / 1000.0

    def run(self):
        while True:
            left_enc_pos = self.robot.left_encoder.get_value()
            right_enc_pos = self.robot.right_encoder.get_value()
            self.odometry.update(left_enc_pos, right_enc_pos, self.dt)

if __name__ == '__main__':
    controller = RobotController()
    controller.run()