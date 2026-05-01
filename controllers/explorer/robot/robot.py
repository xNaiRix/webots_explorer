from controller import Robot as weBots_Robot
from robot.sensors import Sensor
from robot.sensors import Encoder, SensorPS
from typing import List

class Motor:

    pass
class Robot:
    def __init__(self):
        self.robot = weBots_Robot()
        self.basic_time_step = self.robot.getBasicTimeStep()
        self.width = 55
        self.wheel_radius = 20.5
        self.motor = Motor()
        self.left_encoder = Encoder(
            "left wheel sensor", self.basic_time_step)
        self.right_encoder = Encoder(
            "right wheel sensor", self.basic_time_step)
        self.sensors_ps = [
            SensorPS(i,self.basic_time_step) for i in range(8)]

