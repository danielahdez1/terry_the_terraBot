from behavior import *

#sensor data passed into greenhouse tasks:
#  ["time", "coffeesize", "coffeepod", "occupancy"]
#actuators are looking for a dictionary with any/all of these keywords:
#  {"lights":val, "coffee":"on"/"off", "hvac": "on"/"off"}

'''
The lights should be programmed on a dimmer based on the time of day
and whether there are people in the house.
'''
class DimLight(Behavior):

    def __init__(self):
        super(DimLight, self).__init__("DimLightBehavior")
        self.setInitial("halt")

    def setInitial(self, state):
        self.state = state
        self.led = 0
        self.setLED(self.led)

    def enable(self):
        self.setInitial("init")

    def disable(self):
        self.setInitial("halt")

    def perceive(self):
        self.time = self.sensordata["mtime"]
        self.occ = self.sensordata["occupancy"]

    def act(self):
        if self.state == "halt":
            return

        hour = (self.mtime//3600)%24
        if self.occ == 1 and hour >= 15 and hour < 22:
            self.led = 255-((t-15)*15)
            self.setLED(self.led)
        else:
            self.led = 0
            self.setLED(self.led)

    def setLED(self, led):
        self.led = max(0, min(255, led))
        self.actuators.doActions((self.name, self.sensors.getTime(),
                                  {"led": self.led}))


'''
The coffee should be made at 7am and 3pm if there is a pod and there is a size selected
'''
class CoffeeMaker(Behavior):

    def __init__(self):
        super(CoffeeMaker, self).__init__("CoffeeBehavior")
        self.setInitial("halt")

    def setInitial(self, state):
        self.state = state
        self.setCoffee("off")

    def enable(self):
        self.setInitial("init")

    def disable(self):
        self.setInitial("halt")

    def perceive(self):
        self.time = self.sensordata["mtime"]
        self.size = self.sensordata["coffeesize"]
        self.pod = self.sensordata["coffeepod"]

    def act(self):
        if self.state == "halt":
            return

        hour = (self.mtime//3600)%24
        if self.state == "init" and self.size != 0 and pod == 1 and (hour == 7 or hour == 15):
            self.state = "makecoffee"
            self.starttime = self.time
            self.setCoffee("on")
        elif self.state == "makecoffee" and self.time - self.starttime >= 5:
            self.state = "waiting"
            self.setCoffee("off")
        elif self.state == "waiting" and self.time - self.starttime > 60:
            self.state = "init"

    def setCoffee(self, state):
        self.actuators.doActions((self.name, self.sensordata["time"], {"coffee":state}))


'''
The HVAC should be on when people are home
'''
class HVAC(Behavior):

    def __init__(self):
        super(HVAC, self).__init__("HVACBehavior")
        self.setInitial("halt")

    def setInitial(self, state):
        self.state = state
        self.setHVAC("off")

    def enable(self):
        self.setInitial("init")

    def disable(self):
        self.setInitial("halt")

    def perceive(self):
        self.time = self.sensordata["mtime"]
        self.occ = self.sensordata["occupancy"]

    def act(self):
        if self.occ == 1 and self.state == "init":
            self.state = "running"
            self.setHVAC("on")
        elif self.occ == 0 and self.state == "running":
            self.state = "init"
            self.setHVAC("off")


    def setHVAC(self, state):
        self.actuators.doActions((self.name, self.sensordata["time"], {"hvac":state}))
