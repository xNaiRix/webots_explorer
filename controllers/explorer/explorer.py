"""
Главный контроллер робота-разведчика.
Интегрирует все модули: датчики, одометрию, навигацию и FSM.
"""
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

    def run(self):
        self.fsm.run()