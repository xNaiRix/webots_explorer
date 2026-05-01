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
        self.current_speed = 0.
        self.acceleration = 1.
        self.max_speed = 6.283185307179586
        self.device:webots_Motor = self.device
        self.device.setPosition(float('inf'))
        #TODO

    def set_velocity(self, speed_rad:float):
        pass#TODO



class Sensor(ABC, Device):
    def __init__(self, timestep:float, *args):
        super().__init__(*args)
        self.device:webots_Sensor = self.device
        self.device.enable(timestep)
    
    def get_value(self):
        return self.device.getValue()
    
    

class Encoder(Device):
    def init(self):
        pass


class SensorPS(Device):#передается список пс'ов с их нормализованными весами
    def init(self):
        pass#TODO

    def wall_detected(self, lower_threshold, upper_threshold):
        #TODO: по принципу триггера шмидта
        pass

        
