# Class python for serialization JSON

class Consumption:
    def __init__(self, current, voltage, power, frequency):
        self.current = current
        self.voltage = voltage
        self.power = power
        self.frequency = frequency 

class Radio:
    def __init__(self, rssi, frequency):
        self.rssi = rssi
        self.frequency = frequency

class Sensor:
    def __init__(self, temperature, luminosity, frequency):
        self.temperature = temperature
        self.luminosity = luminosity
        self.frequency = frequency

class Profile:
    def __init__(self, profilename=None, power=None, consumption=None, radio=None, sensor=None):
        self.profilename = profilename
        self.power = power
        self.consumption = consumption
        self.radio = radio
        self.sensor = sensor

