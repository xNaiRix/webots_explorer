from typing import Callable
from abc import ABC, abstractmethod
from controller.device import Device as webots_Device
from controller.sensor import Sensor as webots_Sensor
from controller.motor import Motor as webots_Motor


class Device(ABC):
    def __init__(self,
                 getDevice:Callable[[str], webots_Device],
                 device_name:str
                ):
        self.device:webots_Device = getDevice(device_name)
        self.init()
        #TODO

    @abstractmethod
    def init(self):
        pass


class WheelMotor(Device):
    def init(self):
        self.acceleration = 1.
        self.max_speed = 6.283185307179586
        self.device:webots_Motor = self.device
        self.device.setPosition(float('inf'))
        self.current_speed = 0.
        self.device.setVelocity(0.)

    def set_velocity(self, speed_rad:float):
        speed_rad = max(min(speed_rad, self.max_speed), -self.max_speed)
        if speed_rad > self.current_speed:
            self.current_speed = min(speed_rad,
                                     self.current_speed + self.acceleration)
        else:
            self.current_speed = max(speed_rad,
                                     self.current_speed - self.acceleration)
        self.device.setVelocity(self.current_speed)


class Sensor(ABC, Device):
    def __init__(self, timestep:float, *args):
        super().__init__(*args)
        self.device:webots_Sensor = self.device
        self.device.enable(timestep)
    
    def get_value(self):
        return self.device.getValue()
    
    

class Encoder(Sensor):
    def init(self):
        pass


class SensorPS(Sensor):
    def init(self):
        pass


class SchmidtTrigger:
    def __init__(self, lower_threshold:float, upper_threshold:float,
                 sensor_ps_list):
        self.lower_threshold = lower_threshold
        self.upper_threshold = upper_threshold
        self.sensor_ps_list = sensor_ps_list
        self.was_detected = False
    
    def update(self):
        values = [weight * sensor_ps.get_value() for sensor_ps, weight in self.sensor_ps_list]
        mean_value = sum(values)
        if mean_value > self.upper_threshold:
            self.was_detected = True
        if mean_value < self.lower_threshold:
            self.was_detected = False
    
    @property
    def detected(self):
        self.update()
        return self.was_detected