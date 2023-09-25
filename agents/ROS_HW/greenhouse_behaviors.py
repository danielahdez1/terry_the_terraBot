from behavior import *
from limits import *
from lib.terrabot_utils import clock_time

#sensor data passed into greenhouse behaviors:
#  [time, lightlevel, temperature, humidity, soilmoisture, waterlevel]
#actuators are looking for a dictionary with any/all of these keywords:
#  {"led":val, "fan":True/False, "pump": True/False}


'''
The combined ambient and LED light level between 8am and 10pm should be 
in the optimal['light_level'] range;
Between 10pm and 8am, the LEDs should be off (set to 0).
'''
class Light(Behavior):

    def __init__(self):
        super(Light, self).__init__("LightBehavior")
        self.optimal_level = optimal['light_level']
        self.state = "halt"
        
    def setInitial(self, state):
        self.led = 0
        self.setLED(self.led)
        self.state = state
        
    def enable(self):
        self.setInitial("init")
        
    def disable(self):
        self.setInitial("halt")
    
    def perceive(self):
        self.mtime = self.sensordata["midnight_time"]
        self.time = self.sensordata["unix_time"]
        self.light = self.sensordata["light"]
    
    def act(self):
        if self.state == "halt":
            return
            
        hour = (self.mtime//3600)%24
        if hour >= 8 and hour < 22:
            self.state = "light"
            if self.light < self.optimal_level[0]:
                self.setLED(self.led+20)
            elif self.light >= self.optimal_level[1]:
                self.setLED(self.led-20)
        else:
            if self.state != "dark":
                self.state = "dark"
                self.setLED(0)
        
    def setLED(self, led):
        self.led = max(0, min(255, led))
        print("Turning the lights to %d" %self.led)
        self.actuators.doActions((self.name, self.sensors.getTime(),
                                  {"led": self.led}))
                                  
        
'''
The temperature should be greater than the lower limit
'''
class RaiseTemp(Behavior):

    def __init__(self):
        super(RaiseTemp, self).__init__("RaiseTempBehavior") 
        self.state = "halt"
        
    def setInitial(self, state):
        self.state = state
        self.setLED(0)
        
    def enable(self):
        self.setInitial("init")
        
    def disable(self):
        self.setInitial("halt")
        
    def perceive(self):
        self.temp = self.sensordata["temp"]

    def act(self):
        if self.state == "halt":
            return
            
        if self.temp < limits['temperature'][0]:
            self.state = "toolow"
            if self.actuators.actuator_state['led'] < 200:
                self.setLED(200)
                print("Turning up the lights to raise the temperature")
        elif self.temp >= optimal['temperature'][0] and self.state == "toolow":
            self.state = "perfect"
            self.setLED(0)
            print("Temperature is now perfect!")
            
    def setLED(self, level):
        self.actuators.doActions((self.name, self.sensors.getTime(),
                                  {"led": level}))
        
'''
The temperature should be less than the upper limit
'''
class LowerTemp(Behavior):

    def __init__(self):
        super(LowerTemp, self).__init__("LowerTempBehavior") #Behavior sets reasonable defaults
        self.state = "halt"
        
    def setInitial(self, state):
        self.state = state
        self.setFan(False)
        
    def enable(self):
        self.setInitial("init")
        
    def disable(self):
        self.setInitial("halt")
        
    def perceive(self):
        self.temp = self.sensordata["temp"]

    def act(self):
        if self.state == "halt":
            return
            
        if self.temp >= limits['temperature'][1] and self.state != "toohigh":
            self.state = "toohigh"
            self.setFan(True)
            print("Turning on the fan to lower temperature")
        elif self.temp <= optimal['temperature'][1] and self.state == "toohigh":
            self.state = "perfect"
            self.setFan(False)
            print("Temperature is now perfect!")
            
    def setFan(self, act_state):
        self.actuators.doActions((self.name, self.sensors.getTime(),
                                  {"fan": act_state}))
    
'''
Humidity should be less than the limit
'''
class LowerHumid(Behavior):

    def __init__(self):
        super(LowerHumid, self).__init__("LowerHumidBehavior") #Behavior sets reasonable defaults
        self.state = "halt"
        
    def setInitial(self, state):
        self.state = state
        self.setFan(False)
        
    def enable(self):
        self.setInitial("init")
        
    def disable(self):
        self.setInitial("halt")

    def perceive(self):
        self.humid = self.sensordata["humid"]

    def act(self):
        if self.state == "halt":
            return
            
        if self.humid >= limits["humidity"][1] and self.state != "toohumid":
            self.state = "toohumid"
            self.setFan(True)
            print("Turning on the fan to lower humidity")
        elif self.humid <= optimal['humidity'][1] and self.state == "toohumid":
            self.state = "perfect"
            self.setFan(False)
            print("Humidity is now perfect!")

    def setFan(self, act_state):
        self.actuators.doActions((self.name, self.sensors.getTime(),
                                  {"fan": act_state}))
            
'''
Soil moisture should be greater than the lower limit
'''
class RaiseSMoist(Behavior):

    def __init__(self):
        super(RaiseSMoist, self).__init__("RaiseMoistBehavior") #Behavior sets reasonable defaults
        self.state = "halt"
        self.weight = 0
        self.weight_window = []
        self.smoist_window = []
        self.total_water = 0
        self.waterlevel = 0
        self.last_time = 24*60*60 # Start with the prior day
        self.daily_limit = 50 #100
        self.moisture_opt = optimal["moisture"][0]
        
        
    def setInitial(self, state):
        self.state = state
        
    def enable(self):
        self.setInitial("init")
        self.setPump(False)
        self.setTimer(10) # Give the sliding windows time to average out

    def disable(self):
        self.setInitial("halt")
        self.setPump(False)
        self.setLastTime()
        
    def sliding_window(self, window, item, length=4):
        if (len(window) == 0):
            window = [item]*length
        else:
            window = window[1:]
            window.append(item)
        return window, sum(window)/float(length)
    
    def perceive(self):
        self.time = self.sensordata["unix_time"]
        self.mtime = self.sensordata["midnight_time"]
        self.waterLevel = self.sensordata["level"]
        self.weight = self.sensordata["weight"]
        self.weight_window, self.weight_est = self.sliding_window(self.weight_window, self.weight)
        self.smoist = self.sensordata["smoist"]
        self.smoist_window, self.smoist_est = self.sliding_window(self.smoist_window, self.smoist)

    def act(self):
        if self.state == "init":
            if self.last_time > self.mtime: #it's the next day
                print("Next day!")
                self.resetTotalWater()
            elif self.time >= self.waittime: #time is up
                self.state = "waiting"
        elif self.state == "waiting":
            if self.total_water >= self.daily_limit: #watered enough
                self.printWateredEnough()
                self.state = "done"
            elif self.waterLevel < 30: #not enough water in reservoir
                print("NOT ENOUGH WATER IN RESERVOIR")
            elif self.smoist_est >= self.moisture_opt: #soil is moist enough
                print("Soil is moist enough (%s)" %self.smoist_est)
                self.state = "done"
            elif self.smoist_est < self.moisture_opt: #soil is too dry
                print("Soil too dry (%s) - need to water" %self.smoist_est)
                self.start_weight = self.weight_est
                self.setTimer10()
                self.setPump(True)
                self.state = "watering"
        elif self.state == "watering":
            if self.time >= self.waittime: #time is up
               self.setPump(False)
               self.setTimer20()
               self.state = "measuring"
        elif self.state == "measuring":
            if self.time >= self.waittime: #time is up
                self.calcWaterAdded()
                self.state = "waiting"
                
    def setTimer(self, wait):
        self.waittime = self.time + wait
        #print("setTimer: %d (%d)" %(self.waittime, wait))
    def setTimer10(self): self.setTimer(10)
    def setTimer20(self): self.setTimer(20)

    def setLastTime(self): self.last_time = self.mtime
    def resetTotalWater(self): # Reset total water each day
        print("Resetting total water")
        self.total_water = 0
        self.setLastTime()

    def calcWaterAdded(self):
        dwater = self.weight_est - self.start_weight # ml of water weighs a gram
        # Sometimes scales are off - cannot lose weight after watering
        dwater = max(0, dwater)

        self.total_water += dwater
        print("calcWaterAdded: %.1f (%.1f = %.1f - %.1f)"
              %(self.total_water, dwater, self.weight_est, self.start_weight))
        
    def printWateredEnough(self):
        print("Watered Enough: %.1f" %self.total_water)

    def emailNoWater(self): # Email TBD
        print("NOT ENOUGH WATER IN RESERVOIR")

    def setPump(self,state):
        self.actuators.doActions((self.name, self.sensors.getTime(),
                                  {"wpump": state}))
        
'''
Soil moisture below the upper limit
'''
class LowerSMoist(Behavior):

    def __init__(self):
        super(LowerSMoist, self).__init__("LowerMoistBehavior") #Behavior sets reasonable defaults
        self.state = "halt"
        
    def setInitial(self, state):
        self.state = state
        self.setFan(False)
        
    def enable(self):
        self.setInitial("init")
        
    def disable(self):
        self.setInitial("halt")
    
    def perceive(self):
        self.smoist = self.sensordata["smoist"]

    def act(self):
        if self.state == "halt":
            return
            
        if self.smoist >= limits["moisture"][1] and self.state != "toomoist":
            self.state = "toomoist"
            self.setFan(True)
            print("Turning on the fan to lower soil moisture")
        elif self.smoist <= optimal['moisture'][1] and self.state == "toomoist":
            self.state = "perfect"
            self.setFan(False)
            print("Soil moisture is now perfect!")
            
    def setFan(self, act_state):
        self.actuators.doActions((self.name, self.sensors.getTime(),
                                  {"fan": act_state}))
