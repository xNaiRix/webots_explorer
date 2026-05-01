from controller import Robot as weBots_Robot
from robot.devices import WheelMotor, Encoder, SensorPS
import constants

class Robot:
    def __init__(self):
        self.robot = weBots_Robot()
        self.basic_time_step = self.robot.getBasicTimeStep()

        self.__left_motor = WheelMotor(
            self.robot.getDevice,
            "left wheel motor",
        )
        self.__right_motor = WheelMotor(
            self.robot.getDevice,
            "right wheel motor",
        )
        
        self.left_encoder = Encoder(
            self.basic_time_step,
            self.robot.getDevice,
            "left wheel sensor"
        )
        self.right_encoder = Encoder(
            self.basic_time_step,
            self.robot.getDevice,
            "right wheel sensor"
        )
        
        self.sensors_ps = [
            SensorPS(
                self.basic_time_step,
                self.robot.getDevice,
                f"ps{i}",
                ) 
            for i in range(8)]
        
    def step(self) -> bool:
        return self.robot.step(self.basic_time_step) != -1

    def get_time(self) -> float:
        return self.robot.getTime()


    def set_right_velocity(self, speed):#speed - мм
        self.__right_motor.set_velocity(speed/constants.ROBOT_WHEEL_RADIUS)

    def set_left_velocity(self, speed):#speed - мм
        self.__left_motor.set_velocity(speed/constants.ROBOT_WHEEL_RADIUS)


