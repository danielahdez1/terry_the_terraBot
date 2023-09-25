from behavior import *
from limits import *
from transitions import Machine

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
        self.optimal_level = optimal['light_level'] #860,940

        # STUDENT CODE: Modify these lines to use your own initial state name
        #               and add all your FSM states
       
        
        self.initial = 'init'
        self.states = ['init','Night','Day']

        self.fsm = Machine(self, states=self.states, initial=self.initial,
                           ignore_invalid_triggers=True)
  
        # Add FSM transitions and actions
        # BEGIN STUDENT CODE
        
        self.fsm.add_transition('disable','*','init', after="turnOff")
        self.fsm.add_transition('enable','*','init',  after="turnOff")
        self.fsm.add_transition('doStep','init','init', conditions = ['isNight'])
        self.fsm.add_transition('doStep','init','Night', conditions = ['isNight'],  before="turnOff")
        self.fsm.add_transition('doStep','init','Day', conditions = ['isDay'],  before="adjust")
        self.fsm.add_transition('doStep','Day','Day', conditions = ['isDay'],  before="adjust")
        self.fsm.add_transition('doStep','Day','init', conditions = ['isNight'],  before="turnOff")
        
        
  

        # END STUDENT CODE
        
 
    
    def setInitial(self):
        self.led = 0
        self.setLED(self.led)
        
    def perceive(self):
        self.mtime = self.sensordata["midnight_time"]
        self.time = self.sensordata["unix_time"]
        self.light = self.sensordata["light"]
    
    def act(self):
        # Use 'doStep' trigger for all other transitions
        self.trigger("doStep")
        
    # Add all your condition functions here
    # BEGIN STUDENT CODE
    def isDay(self):
        if 28800<=(self.mtime)<79200:
            if self.light<self.optimal_level[0]:
    	        self.change = (self.led +20 )
            elif self.light>=self.optimal_level[1]:
    	        self.change = (self.led-20)
            else:
                self.change = (self.led)
    
        return 28800<=(self.mtime)<79200
        
    def isNight(self):
        return not 28800<=(self.mtime)<79200
        
    # END STUDENT CODE
        
    # Add all your before / after action functions here
    # BEGIN STUDENT CODE
    
    def adjust(self):
    	self.setLED(self.change)
    	  
    def turnOff(self):
        self.setLED(0)

    
    # END STUDENT CODE

    def setLED(self, level):
        self.led = max(0, min(255,level))
        self.actuators.doActions((self.name, self.sensors.getTime(), {"led": self.led}))
                                  

"""
The temperature should be greater than the lower limit
"""
class RaiseTemp(Behavior):

    def __init__(self):
        super(RaiseTemp, self).__init__("RaiseTempBehavior")

        # STUDENT CODE: Modify these lines to use your own initial state name
        #               and add all your FSM states
        self.initial = 'init'
        self.states = ['init','tooLow', 'perfect']

        self.fsm = Machine(self, states=self.states, initial=self.initial,
                           ignore_invalid_triggers=True)

        # Add FSM transitions and actions
        # BEGIN STUDENT CODE
        self.fsm.add_transition('enable','*','init', after="turnOff")
        self.fsm.add_transition('disable','*','init',  after="turnOff")
        self.fsm.add_transition('doStep','init','init', conditions = ['isGood'])
        self.fsm.add_transition('doStep','init','perfect', conditions = ['isGood'],  before="turnOff")
        self.fsm.add_transition('doStep','init','tooLow', conditions = ['isBad'],  before="adjust")
        self.fsm.add_transition('doStep','tooLow','tooLow', conditions = ['isBad'],  before="adjust")
        self.fsm.add_transition('doStep','tooLow','init', conditions = ['isGood'],  before="turnOff")
        # END STUDENT CODE

    
    def isGood(self):
        return self.temp >= optimal['temperature'][0]
    
    def isBad(self):
        return self.temp < limits['temperature'][0]
    
    def adjust(self):
        self.setLED(max(self.led,200))

       
       
    def turnOff(self):
        self.setLED(0)
    
    def setInitial(self):
        self.led = 0
        self.setLED(0)
        
    def perceive(self):
        self.temp = self.sensordata["temp"]

    def act(self):
        # Use 'doStep' trigger for all other transitions
        self.trigger("doStep")

    # Add all your condition functions here
    # BEGIN STUDENT CODE
    
    
    # END STUDENT CODE

    # Add all your before / after action functions here
    # BEGIN STUDENT CODE
    # END STUDENT CODE
            
    def setLED(self, level):
        self.led = max(0, min(255,level))
        self.actuators.doActions((self.name, self.sensors.getTime(),
                                  {"led": level}))
        
"""
The temperature should be less than the upper limit
"""
class LowerTemp(Behavior):

    def __init__(self):
        super(LowerTemp, self).__init__("LowerTempBehavior")

        # STUDENT CODE: Modify these lines to use your own initial state name
        #               and add all your FSM states
        self.initial = 'init'
        self.states = [self.initial,'tooHigh','perfect']

        self.fsm = Machine(self, states=self.states, initial=self.initial,
                           ignore_invalid_triggers=True)

        # Add FSM transitions and actions
        self.fsm.add_transition('enable','*','init', after="setInitial")
        self.fsm.add_transition('disable','*','init',  after="setInitial")
        self.fsm.add_transition('doStep','init','init', conditions = ['isGood'])
        self.fsm.add_transition('doStep','init','perfect', conditions = ['isGood'],  before="setInitial")
        self.fsm.add_transition('doStep','init','tooHigh', conditions = ['isBad'],  before="adjust")
        self.fsm.add_transition('doStep','tooHigh','tooHigh', conditions = ['isBad'],  before="adjust")
        self.fsm.add_transition('doStep','tooHigh','init', conditions = ['isGood'],  before="setInitial")
        
        # BEGIN STUDENT CODE
        # END STUDENT CODE
    
    def isGood(self):
        return self.temp <= optimal['temperature'][1]
    
    def isBad(self):
        return self.temp >= limits['temperature'][1]
    
    def adjust(self):
        self.setFan(True)

        
    def setInitial(self):
        self.setFan(False)
        
    def perceive(self):
        self.temp = self.sensordata["temp"]

    def act(self):
        # Use 'doStep' trigger for all other transitions
        self.trigger("doStep")

    # Add all your condition functions here
    # BEGIN STUDENT CODE
    # END STUDENT CODE
        
    # Add all your before / after action functions here
    # BEGIN STUDENT CODE
    # END STUDENT CODE
            
    def setFan(self, act_state):
        self.actuators.doActions((self.name, self.sensors.getTime(),
                                  {"fan": act_state}))
    
"""
Humidity should be less than the limit
"""
class LowerHumid(Behavior):

    def __init__(self):
        super(LowerHumid, self).__init__("LowerHumidBehavior")

        # STUDENT CODE: Modify these lines to use your own initial state name
        #               and add all your FSM states
        self.initial = 'init'
        self.states = [self.initial,'tooHigh','perfect']

        self.fsm = Machine(self, states=self.states, initial=self.initial,
                           ignore_invalid_triggers=True)

        # Add FSM transitions and actions
        # BEGIN STUDENT CODE
        # END STUDENT CODE
        self.fsm.add_transition('enable','*','init', after="setInitial")
        self.fsm.add_transition('disable','*','init',  after="setInitial")
        self.fsm.add_transition('doStep','init','init', conditions = ['isGood'])
        self.fsm.add_transition('doStep','init','perfect', conditions = ['isGood'],  before="setInitial")
        self.fsm.add_transition('doStep','init','tooHigh', conditions = ['isBad'],  before="adjust")
        self.fsm.add_transition('doStep','tooHigh','tooHigh', conditions = ['isBad'],  before="adjust")
        self.fsm.add_transition('doStep','tooHigh','init', conditions = ['isGood'],  before="setInitial")
        
        # BEGIN STUDENT CODE
        # END STUDENT CODE
    
    def isGood(self):
        return self.humid <= optimal['humidity'][1]
    
    def isBad(self):
        return self.humid >= limits["humidity"][1]
    
    def adjust(self):
        self.setFan(True)
        
    def setInitial(self):
        self.setFan(False)
        
    def perceive(self):
        self.humid = self.sensordata["humid"]

    def act(self):
        # Use 'doStep' trigger for all other transitions
        self.trigger("doStep")

    # Add all your condition functions here
    # BEGIN STUDENT CODE
    # END STUDENT CODE
        
    # Add all your before / after action functions here
    # BEGIN STUDENT CODE
    # END STUDENT CODE

    def setFan(self, act_state):
        self.actuators.doActions((self.name, self.sensors.getTime(),
                                  {"fan": act_state}))
            
"""
Soil moisture should be greater than the lower limit
"""
class RaiseSMoist(Behavior):

    def __init__(self):
        super(RaiseSMoist, self).__init__("RaiseMoistBehavior")
        self.weight = 0
        self.weight_window = []
        self.smoist_window = []
        self.total_water = 0
        self.water_level = 0
        self.start_weight = 0
        self.last_time = 24*60*60 # Start with the prior day
        self.daily_limit = 50 #100
        self.moisture_opt = optimal["moisture"][0]

        # STUDENT CODE: Modify these lines to use your own initial state name
        #               and add all your FSM states
        self.initial = 'init'
        self.states = [self.initial,'waiting','measuring','watering','perfect']
        self.fsm = Machine(self, states=self.states, initial=self.initial,
                           ignore_invalid_triggers=True)

        # Add FSM transitions and actions
        # BEGIN STUDENT CODE
        # END STUDENT CODE
        self.fsm.add_transition('enable','*','init', after="setInitial")
        self.fsm.add_transition('disable','*','init',  after="setInitial")
        self.fsm.add_transition('doStep','init','init', conditions = ['newDay'],after='newDaySetup')
        

        self.fsm.add_transition('doStep','init','waiting', conditions = ['alreadyWaited'])
        self.fsm.add_transition('doStep','waiting','perfect', conditions = ['enoughWater'],after ='sayEnough')
        self.fsm.add_transition('doStep','waiting','perfect', conditions = ['enoughMoist'],after ='sayMoistEnough')
        self.fsm.add_transition('doStep','waiting','waiting', conditions = ['emptyReservoir'], after = 'sayEmptyRes')
        
        self.fsm.add_transition('doStep','waiting','watering', conditions = ['noWater'],after="addWater")
        
        self.fsm.add_transition('doStep','watering','measuring', conditions = ['alreadyWaited'],after="turnOff")
        self.fsm.add_transition('doStep','measuring','waiting', conditions = ['alreadyWaited'],after="doneMeasuring")
        self.fsm.add_transition('doStep','perfect','init', conditions = ['newDay'])
        
        # BEGIN STUDENT CODE
        # END STUDENT CODE
    
    def enoughMoist(self):
        return self.smoist_est >= self.moisture_opt
    def sayMoistEnough(self):
        print("Soil is moist enough (%s)" %self.smoist_est)
    def sayEmptyRes(self):
        print("NOT ENOUGH WATER IN RESERVOIR")
    def sayEnough(self):
        print("Watered Enough: %.1f" %self.total_water)
    def doneMeasuring(self):
        dwater = self.weight_est - self.start_weight
        dwater = max(0, dwater)
        self.total_water += dwater
        
    def turnOff(self):
        self.setPump(False)
        self.setTimer20()
        
        
    def emptyReservoir(self):
        return self.water_level < 30
    
    def alreadyWaited(self):
        return self.time >= self.waittime
    
    
    def addWater(self):
        self.start_weight = self.weight_est
        self.setPump(True)
        self.setTimer10()
        
    def noWater(self):
        return self.smoist_est < self.moisture_opt
    def enoughWater(self):
        return self.total_water >= self.daily_limit
        
    def shouldWait(self):
        return self.time >= self.waittime    
    def newDay(self):
        return self.last_time > self.mtime
    
    def setTimer(self, wait): self.waittime = self.time + wait
    def setTimer10(self): self.setTimer(10)
    def setTimer20(self): self.setTimer(20)
        
    def newDaySetup(self):
        self.total_water = 0
        self.last_time = self.mtime
        
 

    def setInitial(self):
        self.setTimer10()
        self.setPump(False)
        
        
    def sliding_window(self, window, item, length=4):
        if (len(window) == length): window = window[1:]
        window.append(item)
        return window, sum(window)/float(len(window))
    
    def perceive(self):
        self.time = self.sensordata["unix_time"]
        self.mtime = self.sensordata["midnight_time"]
        self.water_level = self.sensordata["level"]
        self.weight = self.sensordata["weight"]
        self.weight_window, self.weight_est = self.sliding_window(self.weight_window, self.weight)
        self.smoist = self.sensordata["smoist"]
        self.smoist_window, self.smoist_est = self.sliding_window(self.smoist_window, self.smoist)

    def act(self):
        # Use 'doStep' trigger for all other transitions
        self.trigger("doStep")

    # Add all your condition functions here
    # BEGIN STUDENT CODE
    # END STUDENT CODE
        
    # Add all your before / after action functions here
    # BEGIN STUDENT CODE
    # END STUDENT CODE

    def setPump(self,state):
        self.actuators.doActions((self.name, self.sensors.getTime(),
                                  {"wpump": state}))

"""
Soil moisture below the upper limit
"""
class LowerSMoist(Behavior):

    def __init__(self):
        super(LowerSMoist, self).__init__("LowerMoistBehavior")


        # STUDENT CODE: Modify these lines to use your own initial state name
        #               and add all your FSM states
        self.initial = 'init'
        self.states = [self.initial,'tooHigh','perfect']

        self.fsm = Machine(self, states=self.states, initial=self.initial,
                           ignore_invalid_triggers=True)

        # Add FSM transitions and actions
        # BEGIN STUDENT CODE
        # END STUDENT CODE
        self.fsm.add_transition('enable','*','init', after="setInitial")
        self.fsm.add_transition('disable','*','init',  after="setInitial")
        self.fsm.add_transition('doStep','init','init', conditions = ['isGood'])
        self.fsm.add_transition('doStep','init','perfect', conditions = ['isGood'],  before="setInitial")
        self.fsm.add_transition('doStep','init','tooHigh', conditions = ['isBad'],  before="adjust")
        self.fsm.add_transition('doStep','tooHigh','tooHigh', conditions = ['isBad'],  before="adjust")
        self.fsm.add_transition('doStep','tooHigh','init', conditions = ['isGood'],  before="setInitial")
        
        # BEGIN STUDENT CODE
        # END STUDENT CODE
    
    def isGood(self):
        return self.smoist <= optimal['moisture'][1]
    
    def isBad(self):
        return self.smoist >= limits["moisture"][1]
    
    def adjust(self):
        self.setFan(True)
        
        
    def setInitial(self):
        self.setFan(False)
        
    def perceive(self):
        self.smoist = self.sensordata["smoist"]

    def act(self):
        # Use 'doStep' trigger for all other transitions
        self.trigger("doStep")

    # Add all your condition functions here
    # BEGIN STUDENT CODE
    # END STUDENT CODE
        
    # Add all your before / after action functions here
    # BEGIN STUDENT CODE
    # END STUDENT CODE
            
    def setFan(self, act_state):
        self.actuators.doActions((self.name, self.sensors.getTime(),
                                  {"fan": act_state}))

