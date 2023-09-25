from behavior import *

'''
The behavior should ping once every 2-3 minutes
'''
class Ping(Behavior):

    def __init__(self):
        super(Ping, self).__init__("PingBehavior")
        self.setInitial("halt")

    def setInitial(self, state):
        self.state = state
        self.last_ping = -10000

    def enable(self):
        self.setInitial("init")

    def disable(self):
        self.setInitial("halt")

    def perceive(self):
        self.time = self.sensordata["unix_time"]

    def act(self):
        if self.time - self.last_ping >= 120:
            self.actuators.doActions((self.name, self.time, {"ping":True}))
            self.last_ping = self.time
