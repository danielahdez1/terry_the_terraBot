from datetime import datetime # Only used "publish"
from transitions import Machine
import logging

class CoffeeMaker:

    def __init__(self):
        self.actions = ['doStep']
        self.sensordata = {'podpresent':False,'smallbuttonpressed':False,
                           'medbuttonpressed':False,'largebuttonpressed':False,
                           'startbuttonpressed': False, 'watertemp':65,
                           'unix_time': 0, 'midnight_time': 0}

        #assumes logging is initialized already
        logging.getLogger('transitions').setLevel(logging.INFO)
        self.sensorlogger = logging.getLogger('sensors')
        self.sensorlogger.setLevel(logging.INFO)
        self.actionlogger = logging.getLogger('actions')
        self.actionlogger.setLevel(logging.INFO)

        self.initial = 'empty'
        # STUDENT CODE: Modify this line to include all your FSM states
        self.states = ['empty','havePod','haveSize', 'ready', 'heat','dispense', 'finished']

        self.fsm = Machine(model=self, states=self.states, initial=self.initial,
                           ignore_invalid_triggers=True)
        # Put all the 'add_transition' calls here
        # BEGIN STUDENT CODE
        self.curSize = None
        
        self.fsm.add_transition('doStep','empty','havePod',conditions=['isPodIn'])
        self.fsm.add_transition('doStep','empty','haveSize',conditions=['isSizeIn'],after='updateSize')
        self.fsm.add_transition('doStep','ready','empty',conditions=['isPodNotIn','isSizeIn'])   
        self.fsm.add_transition('doStep','ready','ready',conditions=['switchedSizes'],after='updateSize')    
        self.fsm.add_transition('doStep','havePod','ready',conditions=['isSizeIn'],after='updateSize')
        self.fsm.add_transition('doStep','haveSize','ready',conditions=['isPodIn'])
        self.fsm.add_transition('doStep','ready','heat',conditions=['isButtonPressed'],after='start_heating')
        self.fsm.add_transition('doStep','heat','dispense',conditions=['gotTo180'],after='start_dispensing')
        self.fsm.add_transition('doStep','dispense','finished',conditions=['enoughTime'],after='done_dispensing')
        self.fsm.add_transition('doStep','finished','empty',conditions=['isPodNotIn'],after='done_dispensing')
        
        # 5,9
        # END STUDENT CODE

    # Add all your condition functions here
    # BEGIN STUDENT CODE

    def switchedSizes(self):
        selectedSize = 0
        if self.sensordata['smallbuttonpressed']:
            selectedSize = 5
        elif self.sensordata['medbuttonpressed']:
    	    selectedSize = 10
        elif self.sensordata['largebuttonpressed']:
    	    selectedSize = 15
    	
        return selectedSize!=self.curSize
        
    	
    def enoughTime(self):
    	time = self.sensordata['unix_time'] - self.timer
    	return time>=self.curSize-1
    	
    def gotTo180(self):
    	return self.sensordata['watertemp']>=180
    	
    def isButtonPressed(self):
    	
    	return self.sensordata['startbuttonpressed']
    	
    def isPodNotIn(self):
    	return not self.sensordata['podpresent']
    
    def isPodIn(self):
    	
    	return self.sensordata['podpresent']
    
    def updateSize(self):
        self.curSize = max(self.sensordata['smallbuttonpressed']*5,self.sensordata['medbuttonpressed']*10,self.sensordata['largebuttonpressed']*15,0)
        
   
    def isSizeIn(self):
    	
    	return (self.sensordata['smallbuttonpressed'] or self.sensordata['medbuttonpressed'] or self.sensordata['largebuttonpressed'])
    	
    # END STUDENT CODE

    # These are the action functions that you should use as
    #    before or after functions
    def start_heating(self):
        self.publish('START HEATING')

    def start_dispensing(self):
        #after publishing this message,
        #insert your code to dispense for a certain amount of time
        #    (not necessarily in this function)
        #hint: use sensordata instead of spinning
        self.timer = self.sensordata['unix_time']
        self.publish('START DISPENSING')

    def done_dispensing(self):
        self.publish('DONE DISPENSING')

    def sense(self, sensordata={}):
        # In case you want to store more data in self.sensordata,
        #   we only write over the data that is sensed externally
        #   plus updating the time variables
        for sensor in sensordata:
            self.sensordata[sensor] = sensordata[sensor]
        self.sensorlogger.info(self.sensordata)

    def act(self):
        self.trigger('doStep')

    def publish(self, message):
        self.action = message
        now = datetime.fromtimestamp(self.sensordata['unix_time'])
        self.actionlogger.info("%s,%s" %(now, message))
         
