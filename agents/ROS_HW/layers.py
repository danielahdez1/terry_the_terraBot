import schedule as sched

class BehavioralLayer:

    def __init__(self, sensors, actuators, behaviors):
        self.behaviors = behaviors
        for behavior in behaviors:
            behavior.setSensors(sensors)
            behavior.setActuators(actuators)
        self.enabled = []
        # Initialize any extra variables here

    def getBehavior(self, name):
        for b in self.behaviors:
            if (b.name == name): return b
        return None

    def isEnabled(self, behavior):
        return behavior in self.enabled

    def startBehavior(self,name):
        # BEGIN STUDENT CODE
        behavior = self.getBehavior(name)
        if behavior and not self.isEnabled(behavior):
            self.enabled.append(behavior)
            behavior.start()
            #print('enablin',self.enabled)
        # END STUDENT CODE
        

    def pauseBehavior(self,name):
        # BEGIN STUDENT CODE
        behavior = self.getBehavior(name)
        if behavior and self.isEnabled(behavior):
            self.enabled.remove(behavior)
            behavior.pause()
        # END STUDENT CODE
        

    def doStep(self):
        for behavior in self.enabled:
            behavior.doStep()

    def startAll(self):
        for behavior in self.behaviors:
            self.startBehavior(behavior.name)

    #more functions? write them here!

class ExecutiveLayer:

    def __init__(self):
        self.schedule = {}
        self.laststep = -1
        self.monitors = []
        # Initialize any extra variables here

    def setPlanningLayer(self, planning):
        self.planning = planning

    def setBehavioralLayer(self, behavioral):
        self.behavioral = behavioral

    def setSchedule(self, schedule):
        self.schedule = schedule

    def requestNewSchedule(self):
        self.planning.requestNewSchedule()

    def getMonitor(self, name):
        for m in self.monitors:
            if (m.name == name): return m
        return None

    def setMonitors(self, sensors, monitorsList):
        self.monitors = monitorsList
        now = sensors.getTime()
        for monitor in self.monitors:
            monitor.setSensors(sensors)
            monitor.setExecutive(self)
            monitor.last_time = now
            monitor.dt = 0
            monitor.activate()

    def doStep(self, t): #t time in seconds since midnight
        # NOTE: Disable any behaviors that need to be disabled
        #   before enabling any new behaviors
        # BEGIN STUDENT CODE
      
        for behavior_name in self.schedule:
            #print(behavior_name,self.schedule[behavior_name])
            doPause = True
            for start,end in self.schedule[behavior_name]:
                #if t<start*60 or t>=end*60:
                if start*60<=t<end*60:
                    doPause = False
                    #break
                    #[1,5],[90,100]
                    
            
            if doPause:
                behavior = self.behavioral.pauseBehavior(behavior_name)


        
        for behavior_name in self.schedule:
            for start,end in self.schedule[behavior_name]:
                if start*60<=t<end*60:
                    self.behavioral.startBehavior(behavior_name)

      
        # END STUDENT CODE
        for monitor in self.monitors:
            monitor.doMonitor()


class PlanningLayer:

    def __init__(self, schedulefile):
        self.schedulefile = schedulefile
        self.usetestfile = False
        self.schedulerequested = True
        self.schedule = {}
        self.laststep = 0

    def setTestingSchedule(self, testschedule):
        self.testschedule = testschedule

    def setExecutive(self, executive):
        self.executive = executive

    def switch_to_test_sched(self):
        self.usetestfile = True
        self.requestNewSchedule()

    def getNewSchedule(self):
        if self.usetestfile:
            self.schedule = self.scheduleFromFile(self.testschedule)
        else:
            self.schedule = self.scheduleFromFile(self.schedulefile)
        self.executive.setSchedule(self.schedule)
        self.schedulerequested = False

    def requestNewSchedule(self):
        self.schedulerequested = True

    def doStep(self, t):
        if self.schedulerequested or self.checkEnded(t):
            self.getNewSchedule()
        self.laststep = (t//60)%(24*60)

    def checkEnded(self, t):
        mins = (t//60)%(24*60)
        if mins < self.laststep: #looped back around
            return True
        return False

    def scheduleFromFile(self, schedulefile):
        schedule = sched.readSchedule(schedulefile)
        return schedule
