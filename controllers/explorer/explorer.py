"""
Главный контроллер робота-разведчика.
Интегрирует все модули: датчики, одометрию, навигацию и FSM.
"""
from robot.robot import Robot
import sys
import os
import csv
import time
from constants import CELL_SIDE, ROBOT_CELL_RADIUS

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from robot import Robot
from robot.devices import SchmidtTrigger
from odometry import Odometry
from FSM.fsm import FSMHandler
from map import Direction, MapPoint, Map

class RobotController:
    def __init__(self):
        self.robot = Robot()
        self.__init_triggers__()
        self.odometry = Odometry(start_x=100.0, start_y=100.0)
        self.map = Map(ROBOT_CELL_RADIUS)
        self.fsm = FSMHandler(self.map)
        self.dt = self.robot.basic_time_step / 1000.0
    
    def __init_triggers__(self):
        self.far_ps0 = SchmidtTrigger(70, 100, [
            (self.robot.sensors_ps[0], 1.0)
        ])
        self.far_ps7 = SchmidtTrigger(70, 100, [
            (self.robot.sensors_ps[7], 1.0)
        ])
        self.far_ps0_7 = SchmidtTrigger(70, 100, [
            (self.robot.sensors_ps[0], 0.5),
            (self.robot.sensors_ps[7], 0.5)
        ])
        self.near_ps0 = SchmidtTrigger(200, 500, [
            (self.robot.sensors_ps[0], 1.0)
        ])
        self.near_ps7 = SchmidtTrigger(200, 500, [
            (self.robot.sensors_ps[7], 1.0)
        ])
        self.near_ps0_7 = SchmidtTrigger(200, 500, [
            (self.robot.sensors_ps[0], 0.5),
            (self.robot.sensors_ps[7], 0.5)
        ])
        self.far_ps1 = SchmidtTrigger(70, 100, [
            (self.robot.sensors_ps[1], 1.0)
        ])
        self.far_ps1_2 = SchmidtTrigger(70, 100, [
            (self.robot.sensors_ps[1], 0.5),
            (self.robot.sensors_ps[2], 0.5)
        ])
        self.far_ps2 = SchmidtTrigger(70, 100, [
            (self.robot.sensors_ps[2], 1.0)
        ])
        self.near_ps1 = SchmidtTrigger(500, 1000, [
            (self.robot.sensors_ps[1], 1.0)
        ])
        self.near_ps1_2 = SchmidtTrigger(200, 500, [
            (self.robot.sensors_ps[1], 0.75),
            (self.robot.sensors_ps[2], 0.25)
        ])
        self.near_ps2 = SchmidtTrigger(500, 1000, [
            (self.robot.sensors_ps[2], 1.0)
        ])
        self.far_ps6 = SchmidtTrigger(70, 100, [
            (self.robot.sensors_ps[6], 1.0)
        ])
        self.far_ps6_5 = SchmidtTrigger(70, 100, [
            (self.robot.sensors_ps[6], 0.5),
            (self.robot.sensors_ps[5], 0.5)
        ])
        self.far_ps5 = SchmidtTrigger(70, 100, [
            (self.robot.sensors_ps[5], 1.0)
        ])
        self.near_ps6 = SchmidtTrigger(500, 1000, [
            (self.robot.sensors_ps[6], 1.0)
        ])
        self.near_ps6_5 = SchmidtTrigger(200, 500, [
            (self.robot.sensors_ps[6], 0.75),
            (self.robot.sensors_ps[5], 0.25)
        ])
        self.near_ps5 = SchmidtTrigger(500, 1000, [
            (self.robot.sensors_ps[5], 1.0)
        ])

    def run(self):
        step = 0
        while self.robot.step():
            step += 1
            time = self.robot.get_time()

            self.mainloop(step, time)

    def mainloop(self, step:int, time:float):
        left_enc_pos = self.robot.left_encoder.get_value()
        right_enc_pos = self.robot.right_encoder.get_value()

        self.odometry.update(left_enc_pos, right_enc_pos, self.dt)
        x, y, theta = self.odometry.position
        point = MapPoint.from_float_coords(x, y)
        direction = Direction.from_angle(theta)

        if point.distance_to_float_coords(x, y) < CELL_SIDE / 4:
            for dx, dy, trigger in (
                (1, -3, self.far_ps0),
                (0, -3, self.far_ps0_7),
                (-1, -3, self.far_ps7),
                (1, -2, self.near_ps0),
                (0, -2, self.near_ps0_7),
                (-1, -2, self.near_ps7),
                (2, 0, self.near_ps2),
                (2, -1, self.near_ps1_2),
                (2, -2, self.near_ps1),
                (3, 0, self.far_ps2),
                (3, -1, self.far_ps1_2),
                (3, -2, self.far_ps1),
                (-2, 0, self.near_ps5),
                (-2, -1, self.near_ps6_5),
                (-2, -2, self.near_ps6),
                (-3, 0, self.far_ps5),
                (-3, -1, self.far_ps6_5),
                (-3, -2, self.far_ps6)
            ):
                viewed_point = point.add_relative(dx, dy, direction)
                if trigger.detected:
                    self.map.set_wall(viewed_point)
                else:
                    self.map.set_empty(viewed_point)
        
        left_velocity, right_velocity = self.fsm.tick()

        self.robot.set_left_velocity(left_velocity)
        self.robot.set_right_velocity(right_velocity)
                


if __name__ == '__main__':
    controller = RobotController()
    controller.run()