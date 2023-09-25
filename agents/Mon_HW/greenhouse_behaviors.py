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
        self.optimal_level = optimal['light_level']

        # STUDENT CODE: Modify these lines to use your own initial state name
        #               and add all your FSM states
        self.initial = 'initial'
        self.states = [self.initial, 'post_halt', 'light', 'dark']

        self.fsm = Machine(self, states=self.states, initial=self.initial,
                           ignore_invalid_triggers=True)

        # Add FSM transitions and actions
        # BEGIN STUDENT CODE
        self.fsm.add_transition(trigger='enable', source=self.initial, dest='post_halt',
            after='setInitial')

        self.fsm.add_transition(trigger='doStep', source='post_halt', dest='light',
            conditions=["need_lights_on"],after='increase_light')
        self.fsm.add_transition(trigger='doStep', source='post_halt', dest='dark',
            conditions=["need_lights_off"],after='lights_off')

        self.fsm.add_transition(trigger='doStep', source='light', dest='dark', 
            conditions=["need_lights_off"], after='lights_off')
        self.fsm.add_transition(trigger='doStep', source='dark', dest='light', 
            conditions=["need_lights_on","need_to_increase_light"],after='increase_light')

        self.fsm.add_transition(trigger='doStep', source='dark', dest='light', 
            conditions=["need_lights_on"])
        self.fsm.add_transition(trigger='doStep', source='light', dest='light', 
            conditions=["need_lights_on","need_to_increase_light"], after="increase_light")

        self.fsm.add_transition(trigger='doStep', source='light', dest='light', 
            conditions=["need_lights_on","need_to_decrease_light"], after="decrease_light")
        self.fsm.add_transition(trigger='doStep', source='light', dest='light', 
            conditions=["need_lights_on"])

        self.fsm.add_transition(trigger='disable', source='light', dest=self.initial)
        self.fsm.add_transition(trigger='disable', source='dark', dest=self.initial)
        # END STUDENT CODE
        
    def setInitial(self):
        self.led = 0
        self.setLED(self.led)
        
    def perceive(self):
        self.mtime = self.sensordata["midnight_time"]
        self.time = self.sensordata["unix_time"]
        self.light = self.sensordata["light"]

    def update_optimal(self):
        self.optimal_level = optimal['light_level']

    
    def act(self):
        # Use 'doStep' trigger for all other transitions
        self.trigger("doStep")
        
    # Add all your condition functions here
    # BEGIN STUDENT CODE
    def need_lights_on(self):
        # on between 8am and 10pm
        hour = (self.mtime//3600)%24
        return hour >= 8 and hour < 22

    def need_lights_off(self):
        # off between 10pm and 8am
        hour = (self.mtime//3600)%24
        return not (hour >= 8 and hour < 22)

    def need_to_increase_light(self):
        return self.light < self.optimal_level[0]

    def need_to_decrease_light(self):
        return self.light >= self.optimal_level[1]
    # END STUDENT CODE
        
    # Add all your before / after action functions here
    # BEGIN STUDENT CODE
    def increase_light(self):
        self.setLED(self.led+20)

    def decrease_light(self):
        self.setLED(self.led-20)

    def lights_off(self):
        self.setLED(0)
    # END STUDENT CODE

    def setLED(self, level):
        self.led = max(0, min(255, level))
        self.actuators.doActions((self.name, self.sensors.getTime(),  {"led": self.led}))  

"""
The temperature should be greater than the lower limit
"""
class RaiseTemp(Behavior):

    def __init__(self):
        super(RaiseTemp, self).__init__("RaiseTempBehavior")

        # STUDENT CODE: Modify these lines to use your own initial state name
        #               and add all your FSM states
        self.initial = 'initial'
        self.states = [self.initial, 'post_initial', 'low', 'good']

        self.fsm = Machine(self, states=self.states, initial=self.initial,
                           ignore_invalid_triggers=True)

        # Add FSM transitions and actions
        # BEGIN STUDENT
        self.fsm.add_transition(trigger='enable', source='initial', dest='post_initial',
            after='setInitial')

        self.fsm.add_transition(trigger='doStep', source='post_initial', dest='low',
            conditions=["temp_is_low"], after="raise_temp")
        self.fsm.add_transition(trigger='doStep', source='post_initial', dest='good',
            conditions=["temp_good"], after="lower_temp")

        self.fsm.add_transition(trigger='doStep', source='low', dest='good',
            conditions=["temp_good"], after="lower_temp")
        self.fsm.add_transition(trigger='doStep', source='good', dest='low',
            conditions=["temp_is_low"], after="raise_temp")

        self.fsm.add_transition(trigger="disable", source="*", dest="initial")
        # END STUDENT CODE

    def setInitial(self):
        self.setLED(0)
        
    def perceive(self):
        self.temp = self.sensordata["temp"]

    def act(self):
        # Use 'doStep' trigger for all other transitions
        self.trigger("doStep")

    # Add all your condition functions here
    # BEGIN STUDENT CODE
    def temp_is_low(self):
        return self.temp < limits['temperature'][0]

    def temp_good(self):
        return self.temp >= optimal['temperature'][0]
    # END STUDENT CODE

    # Add all your before / after action functions here
    # BEGIN STUDENT CODE
    def raise_temp(self):
        self.setLED(200)

    def lower_temp(self):
        self.setLED(0)
    # END STUDENT CODE
            
    def setLED(self, level):
        self.actuators.doActions((self.name, self.sensors.getTime(),  {"led": level}))
        
"""
The temperature should be less than the upper limit
"""
class LowerTemp(Behavior):

    def __init__(self):
        super(LowerTemp, self).__init__("LowerTempBehavior")

        # STUDENT CODE: Modify these lines to use your own initial state name
        #               and add all your FSM states
        self.initial = 'initial'
        self.states = [self.initial, 'post_initial', 'high', 'good']

        self.fsm = Machine(self, states=self.states, initial=self.initial,
                           ignore_invalid_triggers=True)

        # Add FSM transitions and actions
        # BEGIN STUDENT CODE
        self.fsm.add_transition(trigger='enable', source='initial', dest='post_initial',
            after='setInitial')

        self.fsm.add_transition(trigger='doStep', source='post_initial', dest='high', 
            conditions=["temp_is_high"], after="turn_fan_on")
        self.fsm.add_transition(trigger='doStep', source='high', dest='good', 
            conditions=["temp_good"], after="turn_fan_off")
        self.fsm.add_transition(trigger='doStep', source='good', dest='high', 
            conditions=["temp_is_high"], after="turn_fan_on")

        self.fsm.add_transition(trigger='disable', source='*', dest='initial')
        # END STUDENT CODE

    def setInitial(self):
        self.setFan(False)
        
    def perceive(self):
        self.temp = self.sensordata["temp"]

    def act(self):
        # Use 'doStep' trigger for all other transitions
        self.trigger("doStep")

    # Add all your condition functions here
    # BEGIN STUDENT CODE
    def temp_is_high(self):
        return self.temp >= limits['temperature'][1]

    def temp_good(self):
        return self.temp <= optimal['temperature'][1]
    # END STUDENT CODE

    # Add all your before / after action functions here
    # BEGIN STUDENT CODE
    def turn_fan_on(self):
        self.setFan(True)

    def turn_fan_off(self):
        self.setFan(False)
    # END STUDENT CODE
            
    def setFan(self, act_state):
        self.actuators.doActions((self.name, self.sensors.getTime(),  {"fan": act_state}))
    
"""
Humidity should be less than the limit
"""
class LowerHumid(Behavior):

    def __init__(self):
        super(LowerHumid, self).__init__("LowerHumidBehavior")

        # STUDENT CODE: Modify these lines to use your own initial state name
        #               and add all your FSM states
        self.initial = 'initial'
        self.states = [self.initial, 'post_initial', 'humid', 'good']

        self.fsm = Machine(self, states=self.states, initial=self.initial,
                           ignore_invalid_triggers=True)

        # Add FSM transitions and actions
        # BEGIN STUDENT CODE
        self.fsm.add_transition(trigger='enable', source='initial', dest='post_initial',
            after='setInitial')

        self.fsm.add_transition(trigger='doStep', source='post_initial', dest='humid', 
            conditions=["humidity_is_high"], after="turn_fan_on")
        self.fsm.add_transition(trigger='doStep', source='humid', dest='good', 
            conditions=["humidity_is_good"], after="turn_fan_off")
        self.fsm.add_transition(trigger='doStep', source='good', dest='humid', 
            conditions=["humidity_is_high"], after="turn_fan_on")

        self.fsm.add_transition(trigger='disable', source='*', dest='initial')
        # END STUDENT CODE
        
    def setInitial(self):
        self.setFan(False)
        
    def perceive(self):
        self.humid = self.sensordata["humid"]

    def act(self):
        # Use 'doStep' trigger for all other transitions
        self.trigger("doStep")

    # Add all your condition functions here
    # BEGIN STUDENT CODE
    def humidity_is_high(self):
        return self.humid >= limits['humidity'][1]

    def humidity_is_good(self):
        return self.humid <= optimal['humidity'][1]
    # END STUDENT CODE

    # Add all your before / after action functions here
    # BEGIN STUDENT CODE
    def turn_fan_on(self):
        self.setFan(True)

    def turn_fan_off(self):
        self.setFan(False)
    # END STUDENT CODE

    def setFan(self, act_state):
        self.actuators.doActions((self.name, self.sensors.getTime(),  {"fan": act_state}))
            
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
        self.halt = 'halt'
        self.states = [self.halt, 'initial', 'done', 'waiting',
        'watering', 'measuring']
        self.fsm = Machine(self, states=self.states, initial=self.halt,
                           ignore_invalid_triggers=True)

        # Add FSM transitions and actions
        # BEGIN STUDENT CODE
        self.fsm.add_transition(trigger='enable', source='halt', dest='initial',
            after=['set_pump_F','set_time_10'])
        self.fsm.add_transition(trigger='disable', source='*', dest='halt',
            after=['set_pump_F','set_last_time'])

        self.fsm.add_transition(trigger='doStep', source='initial', dest='initial', 
            conditions=['next_day'], after=['reset_water'])
        self.fsm.add_transition(trigger='doStep', source='initial', dest='waiting', 
            conditions=['timer_done'])

        self.fsm.add_transition(trigger='doStep', source='waiting', dest='done', 
            conditions=['saturated'], after=['print_watered'])
        self.fsm.add_transition(trigger='doStep', source='waiting', dest='done', 
            conditions=['not_enough_water'])
        self.fsm.add_transition(trigger='doStep', source='waiting', dest='done', 
            conditions=['good_moisture'], after=['print_moist'])
        self.fsm.add_transition(trigger='doStep', source='waiting', dest='watering', 
            conditions=['dry_soil'], after=['set_time_10','set_pump_T','reset_weight'])


        self.fsm.add_transition(trigger='doStep', source='watering', dest='measuring', 
            conditions=['timer_done'], after=['set_pump_F', 'set_time_20'])

        self.fsm.add_transition(trigger='doStep', source='measuring', dest='waiting', 
            conditions=['timer_done'], after=['get_total_water'])
        

    def setInitial(self):
        pass
        
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
    def next_day(self):
        return self.last_time > self.mtime

    def not_enough_water(self):
        return self.water_level < 30

    def saturated(self):
        return self.total_water >= self.daily_limit

    def dry_soil(self):
        return self.smoist_est < optimal['moisture'][0]

    def in_prog(self):
        return self.in_progress

    def timer_done(self):
        return self.time >= self.waittime

    def good_moisture(self):
        return self.smoist_est >= optimal['moisture'][0]
    # END STUDENT CODE
        
    # Add all your before / after action functions here
    # BEGIN STUDENT CODE
    def set_time(self, wait):
        self.waittime = self.time + wait
        print("setTimer: %d (%d)" % (self.waittime, wait))

    def set_time_10(self): self.set_time(10)
    def set_time_20(self): self.set_time(20)
    def set_time_30(self): self.set_time(30)
    def set_time_300(self): self.set_time(300)

    def set_water_level(self):
        print("Set water level: %d" % self.water_level)
        self.waterlevel = self.water_level

    def set_last_time(self): self.last_time = self.mtime

    def reset_water(self):  # Reset total water each day
        print("Resetting total water")
        self.total_water = 0
        self.set_last_time()

    def set_in_prog(self): self.in_progress = True
    def reset_in_prog(self): self.in_progress = False

    def get_total_water(self):
        dwater = self.weight_est - self.start_weight
        dwater = max(0, dwater)
        self.total_water += dwater
        print("calcTotalWater: %.1f (%.1f)" % (self.total_water, dwater))

    def print_watered(self): print(
        "Watered Enough: %.1f" % self.total_water)
    def print_moist(self): print(
        "Moist Enough: %.1f" % self.smoist_est)

    def print_in_prog(self): print("In progress: %.1f" % self.smoist_est)
    def print_test(self): print("Testing")

    def set_pump_F(self):
        self.setPump(False)
    def set_pump_T(self):
        self.setPump(True)

    def reset_weight(self):
        print("Soil too dry (%s) - need to water" %self.smoist_est)
        self.start_weight = self.weight_est
    # END STUDENT CODE

    def setPump(self,state):
        self.actuators.doActions((self.name, self.sensors.getTime(),  {"wpump": state}))

"""
Soil moisture below the upper limit
"""
class LowerSMoist(Behavior):

    def __init__(self):
        super(LowerSMoist, self).__init__("LowerMoistBehavior")


        # STUDENT CODE: Modify these lines to use your own initial state name
        #               and add all your FSM states
        self.initial = 'initial'
        self.states = [self.initial, 'post_initial', 'moist', 'good']

        self.fsm = Machine(self, states=self.states, initial=self.initial,
                           ignore_invalid_triggers=True)

        # Add FSM transitions and actions
        # BEGIN STUDENT 
        self.fsm.add_transition(trigger='enable', source='initial', dest='post_initial',
            after='setInitial')

        self.fsm.add_transition(trigger='doStep', source='post_initial', dest='moist', 
            conditions=["moist_is_high"], after="turn_fan_on")
        self.fsm.add_transition(trigger='doStep', source='moist', dest='good', 
            conditions=["moist_good"], after="turn_fan_off")
        self.fsm.add_transition(trigger='doStep', source='good', dest='moist', 
            conditions=["moist_is_high"], after="turn_fan_on")

        self.fsm.add_transition(trigger='disable', source='*', dest='initial')
        # END STUDENT CODE
        
    def setInitial(self):
        self.setFan(False)
        
    def perceive(self):
        self.smoist = self.sensordata["smoist"]

    def act(self):
        # Use 'doStep' trigger for all other transitions
        self.trigger("doStep")

    # Add all your condition functions here
    def moist_is_high(self):
        return self.smoist >= limits['moisture'][1]

    def moist_good(self):
        return self.smoist <= optimal['moisture'][1]
    # END STUDENT CODE

    # Add all your before / after action functions here
    # BEGIN STUDENT CODE
    def turn_fan_on(self):
        self.setFan(True)

    def turn_fan_off(self):
        self.setFan(False)
    # END STUDENT CODE
            
    def setFan(self, act_state):
        self.actuators.doActions((self.name, self.sensors.getTime(),  {"fan": act_state}))
        