from machine import ADC, Pin

# Max ADC value for 16-bit resolution (0-65535)
ADC_MAX = 65535

'''
This module defines the Inputs class for reading potentiometer values and a switch state.
''' 
class Inputs:
    def __init__(self, pot1_pin=26, pot2_pin=27, pot3_pin=28, sw_pin=5):
        self.pot1 = ADC(pot1_pin)
        self.pot2 = ADC(pot2_pin)
        self.pot3 = ADC(pot3_pin)
        self.sw = Pin(sw_pin, Pin.IN, Pin.PULL_UP)
        
    def adc_norm(self, adc_obj):
        return adc_obj.read_u16() / ADC_MAX

    def read(self):
        x1 = self.adc_norm(self.pot1)
        x2 = self.adc_norm(self.pot2)
        x3 = self.adc_norm(self.pot3)
        mode = (self.sw.value() == 1)
        return mode, x1, x2, x3
