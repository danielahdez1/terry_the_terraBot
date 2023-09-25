from behavior import *
from transitions import Machine

'''
The behavior should ping once every 2-3 minutes
'''
class Ping(Behavior):

    def __init__(self):
        super(Ping, self).__init__("PingBehavior")
        self.initial = 'init'
        # STUDENT CODE: Modify these lines to add all your FSM states
        self.states = [self.initial,'wait','ping']

        self.fsm = Machine(self, states=self.states, initial=self.initial,
                           ignore_invalid_triggers=True)

        # Add FSM transitions and actions
        # BEGIN STUDENT CODE
        # END STUDENT CODE
        self.fsm.add_transition('enable','*','init', after="setInitial")
        self.fsm.add_transition('disable','*','init',  after="setInitial")
        self.fsm.add_transition('doStep','init','init', conditions = ['isGood'])
        self.fsm.add_transition('doStep','init','wait', conditions = ['isGood'],  before="setInitial")
        self.fsm.add_transition('doStep','init','ping', conditions = ['isBad'],  before="adjust")
        self.fsm.add_transition('doStep','ping','ping', conditions = ['isBad'],  before="adjust")
        self.fsm.add_transition('doStep','ping','init', conditions = ['isGood'],  before="setInitial")
        
        # BEGIN STUDENT CODE
        # END STUDENT CODE
    
    def isGood(self):
        return self.time - self.last_ping < 120
    
    def isBad(self):
        return self.time - self.last_ping >= 120
    
    def adjust(self):
        self.ping()

    def setInitial(self):
        self.last_ping = -10000

    def perceive(self):
        self.time = self.sensordata["unix_time"]

    def act(self):
        # Use 'doStep' trigger for all other transitions
        self.trigger('doStep')

    # Add all your condition functions here
    # BEGIN STUDENT CODE
    # END STUDENT CODE

    # Add all your before / after action functions here
    # BEGIN STUDENT CODE
    # END STUDENT CODE

    def ping(self):
        self.actuators.doActions((self.name, self.time, {"ping":True}))
        self.last_ping = self.time

