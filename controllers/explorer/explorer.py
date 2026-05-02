import math
print(__file__)
from robot.robot import Robot
from logger import Logger

import sys
import os
from constants import CELL_SIDE, ROBOT_CELL_RADIUS, MAX_COORD_ERROR

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from robot.devices import SchmidtTrigger
from odometry import Odometry
from FSM.fsm import FSMHandler
from map import Direction, MapPoint, Map

k = 0.8915

class RobotController:
    def __init__(self):
        self.robot:Robot = Robot()
        self.__init_triggers__()
        start_x = 100 * CELL_SIDE
        start_y = 100 * CELL_SIDE
        self.odometry = Odometry(start_x=start_x, start_y=start_y)
        self.map = Map(ROBOT_CELL_RADIUS)
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                if abs(dx) != 2 or abs(dy) != 2:
                    self.map.set_empty(MapPoint(int(start_x / CELL_SIDE) + dx, int(start_y / CELL_SIDE) + dy))
        self.fsm = FSMHandler(self.map)
        self.dt = self.robot.basic_time_step / 1000.0
        self.logger = Logger()
    
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

    def run(self, time_period:float):
        step = 0
        start_time = self.robot.get_time()
        while self.robot.get_time() - start_time < time_period and self.robot.step():
            step += 1
            time = self.robot.get_time()

            result = self.mainloop(step, time)
            if not result: break
        
        self.map.print()
        self.map.save_to_file()

    def mainloop(self, step:int, time:float):
        left_enc_pos = k*self.robot.left_encoder.get_value()
        right_enc_pos = k*self.robot.right_encoder.get_value()

        self.odometry.update(left_enc_pos, right_enc_pos, self.dt)
        x, y, theta = self.odometry.position
        point = MapPoint.from_float_coords(x, y)
        direction = Direction.from_angle(theta)

        if (point.distance_to_float_coords(x, y) < MAX_COORD_ERROR) \
        and (abs((theta + math.pi/4) % (math.pi/2) - math.pi/4) < 0.1):
            for dx, dy, trigger in (
                (1, 3, self.far_ps0),
                (0, 3, self.far_ps0_7),
                (-1, 3, self.far_ps7),
                (1, 2, self.near_ps0),
                (0, 2, self.near_ps0_7),
                (-1, 2, self.near_ps7),
                (2, 0, self.near_ps2),
                (2, 1, self.near_ps1_2),
                (2, 2, self.near_ps1),
                (3, 0, self.far_ps2),
                (3, 1, self.far_ps1_2),
                (3, 2, self.far_ps1),
                (-2, 0, self.near_ps5),
                (-2, 1, self.near_ps6_5),
                (-2, 2, self.near_ps6),
                (-3, 0, self.far_ps5),
                (-3, 1, self.far_ps6_5),
                (-3, 2, self.far_ps6)
            ):
                viewed_point = point.add_relative(dx, dy, direction)
                if trigger.detected:
                    self.map.set_wall(viewed_point)
                else:
                    self.map.set_empty(viewed_point)
        
        t = self.fsm.tick(x,y,theta,point,direction)
        if t is None:
            self.robot.set_left_velocity(0)
            self.robot.set_right_velocity(0)
            return False
        left_velocity, right_velocity = t

        self.robot.set_left_velocity(left_velocity)
        self.robot.set_right_velocity(right_velocity)

        self.logger.log_odometry(step, time, x, y, theta)
        self.logger.log_sensors(step, time, self.robot.sensors_ps)

        return True


if __name__ == '__main__':
    controller = RobotController()
    time_period = 30 * 60
    controller.run(time_period)