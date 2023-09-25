from hardware import *
import greenhouse_behaviors, ping_behavior

day_seconds = 60*60*24

class TestSensors(Sensors):
    def __init__(self):
        self.sensors = None

    def setSense(self,sensors):
        self.sensors = sensors

    def doSense(self):
        return self.sensors

    def getTime(self):
        return self.sensors['unix_time']

class TestActuators(Actuators):

    def __init__(self):
        self.actions = None

    def doActions(self, actions):
        #self.actions = [1, 2, {"led": 0}] #actions
        self.actions = actions

def checkPingBehavior(pb):
    ts = TestSensors()
    ta = TestActuators()
    pb.setSensors(ts)
    pb.setActuators(ta)

    assert(ta.actions == None), "Unexpected actions set"
    ts.setSense({"unix_time":0, "midnight_time":0})
    pb.start()

    for t in range(0,10000):
        ts.setSense({"unix_time":t, "midnight_time":t%day_seconds})
        pb.doStep()
        s = "Ping Error: difference between unix_time and last ping > 180 seconds"
        assert t - (ta.actions[1] if ta.actions else 0) <= 60*3, s


def checkLightBehavior3Days(lb):
    lights = [200, 250, 300, 350, 450, 500, 550, 600, 650, 700, 750, 800, 900,
              950, 800, 810, 820, 830, 840, 850, 860, 870, 880, 850, 840, 870,
              990, 950, 940, 920, 800, 820, 900, 950, 750, 850, 900, 860, 870,
              880, 840, 830, 820, 810, 750, 700, 600, 500]
    correct = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 20, 40, 60, 80,
               80, 80, 80, 100, 120, 120, 100, 80, 60, 60, 80, 100, 100, 80,
               100, 120, 120, 120, 120, 120, 140, 160, 180, 200, 0, 0, 0, 0,
               0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 20, 40, 60, 80,
               80, 80, 80, 100, 120, 120, 100, 80, 60, 60, 80, 100, 100, 80,
               100, 120, 120, 120, 120, 120, 140, 160, 180, 200, 0, 0, 0, 0, 0,
               0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 20, 40, 60, 80, 80,
               80, 80, 100, 120, 120, 100, 80, 60, 60, 80, 100, 100, 80, 100,
               120, 120, 120, 120, 120, 140, 160, 180, 200, 0, 0, 0, 0]
    t = 0
    dtime = 1800

    ts = TestSensors()
    ta = TestActuators()
    lb.setSensors(ts)
    lb.setActuators(ta)

    assert(ta.actions == None), "Unexpected action set"
    ts.setSense({"unix_time":0, "midnight_time":0, "light": lights[0]})
    lb.start()
    assert(ta.actions and ta.actions[2] == {"led":0}), "LEDs not turned off initially"

    for i in range(0,48*3):
        t = dtime*i
        ts.setSense({"unix_time":t,
                "midnight_time":t%day_seconds,
                "light": lights[(t%day_seconds)//dtime]})
        lb.doStep()
        s = "Light Error: LED settings not correct. Lights were "+(str(correct[((t%day_seconds)//dtime)-1]) if t > 0 else str(0))+" and the behavior received light value "+str(ts.sensors['light'])+" at time after midnight "+str(t%day_seconds)+" so new LED setting should be "+str(correct[(t%day_seconds)//dtime])+". You sent "+str(ta.actions[2]['led'])
        assert ta.actions and ta.actions[2]['led'] == correct[(t%day_seconds)//dtime],s
        
def checkLightBehaviorDisable(lb):
    lights = [200, 250, 300, 350, 450, 500, 550, 600, 650, 700, 750, 800, 900,
              950, 800, 810, 820, 830, 840, 850, 860, 870, 880, 850, 840, 870,
              990, 950, 940, 920, 800, 820, 900, 950, 750, 850, 900, 860, 870,
              880, 840, 830, 820, 810, 750, 700, 600, 500]
    correct = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 20, 40, 60, 80,
               80, 80, 80, 100, 120, 120, 100, 80, 60, 60, 80, 100, 100, 80,
               100, 120, 120, 120, 120, 120, 140, 160, 180, 200, 0, 0, 0, 0, 0,
               0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 20, 40, 60, 80, 80,
               80, 80, 100, 120, 120, 100, 80, 60, 60, 80, 100, 100, 80, 100,
               120, 120, 120, 120, 120, 140, 160, 180, 200, 0, 0, 0, 0, 0, 0,
               0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 20, 40, 60, 80, 80,
               80, 80, 100, 120, 120, 100, 80, 60, 60, 80, 100, 100, 80, 100,
               120, 120, 120, 120, 120, 140, 160, 180, 200, 0, 0, 0, 0]
    t = 0
    dtime = 1800

    ts = TestSensors()
    ta = TestActuators()
    lb.setSensors(ts)
    lb.setActuators(ta)

    assert(ta.actions == None), "Unexpected action set"
    ts.setSense({"unix_time":0, "midnight_time":0, "light": lights[0]})

    for j in range(3):
        lb.start()
        assert(ta.actions and ta.actions[2] == {"led":0}), "LEDs not turned off initially"

        for i in range(40):
            t = dtime*(i+(j*48))
            ts.setSense({"unix_time":t,
                         "midnight_time":t%day_seconds,
                         "light": lights[i]})
            lb.doStep()
            s = "Light Error: LED settings not correct. Lights were "+(str(correct[i-1]) if i > 0 else str(0))+" and the behavior received light value "+str(ts.sensors['light'])+" at time after midnight "+str(t%day_seconds)+" so new LED setting should be "+str(correct[i])+". You sent "+str(ta.actions[2]['led'])+". Maybe you are not handing disable/enable correctly?"
            assert ta.actions and ta.actions[2]['led'] == correct[i], s

        lb.disable()
        

def checkLowerTempBehavior3Days(ltb):
    temp = [20, 25, 26, 31, 30, 29, 28, 27, 26, 25, 24, 23, 22, 21, 20, 19, 18,
            17, 16, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
            30, 31, 32, 31, 30, 29, 28, 27, 26, 25, 24, 23, 22, 21]
    correct = [False, False, False, True, True, True, True, False, False,
               False, False, False, False, False, False, False, False, False,
               False, False, False, False, False, False, False, False, False,
               False, False, False, False, False, False, True, True, True,
               True, True, True, True, True, False, False, False, False,
               False, False, False]
    t = 0
    dtime = 1800

    ts = TestSensors()
    ta = TestActuators()
    ltb.setSensors(ts)
    ltb.setActuators(ta)

    assert(ta.actions == None), "Unexpected action set"
    ts.setSense({"unix_time":0, "midnight_time":0, "temp": temp[0]})
    ltb.start()
    assert(ta.actions and ta.actions[2] == {"fan":False}), "Fan not turned off initially"
    
    for j in range(3):
        for i in range(48):
            t = dtime*(i+(j*48))
            ts.setSense({"unix_time":t,
                         "midnight_time":t%day_seconds,
                         "temp": temp[i]})
            ltb.doStep()
            s = "LowerTemp Error: Fan settings not correct. Fans were set to "+(str(correct[i-1]) if i > 0 else str(False))+" and the behavior received temp value "+str(ts.sensors['temp'])+" at time after midnight "+str(t%day_seconds)+" so new Fan setting should be "+str(correct[i])+". You sent "+str(ta.actions[2]['fan'])+"."
            assert ta.actions and ta.actions[2]['fan'] == correct[i], s

        
def checkLowerTempBehaviorDisable(ltb):
    temp = [20, 25, 26, 31, 30, 29, 28, 27, 26, 25, 24, 23, 22, 21, 20, 19, 18,
            17, 16, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
            30, 31, 32, 31, 30, 29, 28, 27, 26, 25, 24, 23, 22, 21]
    correct = [False, False, False, True, True, True, True, False, False,
               False, False, False, False, False, False, False, False, False,
               False, False, False, False, False, False, False, False, False,
               False, False, False, False, False, False, True, True, True,
               True, True, True, True, True, False, False, False, False,
               False, False, False]
    t = 0
    dtime = 1800

    ts = TestSensors()
    ta = TestActuators()
    ltb.setSensors(ts)
    ltb.setActuators(ta)

    assert(ta.actions == None), "Unexpected action set"
    ts.setSense({"unix_time":0, "midnight_time":0, "temp": temp[0]})

    for j in range(3):
        ltb.start()
        assert(ta.actions and ta.actions[2] == {"fan":False}), "Fan not turned off initially"

        for i in range(40):
            t = dtime*(i+(j*48))
            ts.setSense({"unix_time":t,
                         "midnight_time":t%day_seconds,
                         "temp": temp[i]})
            ltb.doStep()
            s = "LowerTemp Error: Fan settings not correct. Fans were set to "+(str(correct[i-1]) if i > 0 else str(False))+" and the behavior received temp value "+str(ts.sensors['temp'])+" at time after midnight "+str(t%day_seconds)+" so new Fan setting should be "+str(correct[i])+". You sent "+str(ta.actions[2]['fan'])+". Maybe you are not handing disable/enable correctly?"
            assert ta.actions and ta.actions[2]['fan'] == correct[i], s

        ltb.disable()

        
def checkRaiseTempBehavior3Days(rtb):
    temp = [20, 25, 26, 31, 30, 29, 28, 27, 26, 25, 24, 23, 22, 21, 20, 19, 18,
            17, 16, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
            30, 31, 32, 31, 30, 29, 28, 27, 26, 25, 24, 23, 22, 21]
    correct = [200, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 200, 200, 200, 200,
               200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 0,
               0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 200]
    t = 0
    dtime = 1800

    ts = TestSensors()
    ta = TestActuators()
    rtb.setSensors(ts)
    rtb.setActuators(ta)

    assert(ta.actions == None), "Unexpected action set"
    ts.setSense({"unix_time":0, "midnight_time":0, "temp": temp[0]})
    rtb.start()
    assert(ta.actions and ta.actions[2] == {"led":0}), "LEDs not turned off initially"
    
    for j in range(3):
        for i in range(48):
            t = dtime*(i+(j*48))
            ts.setSense({"unix_time":t,
                         "midnight_time":t%day_seconds,
                         "temp": temp[i]})
            rtb.doStep()
            s = "RaiseTemp Error: LED settings not correct. LEDs were set to "+(str(correct[i-1]) if i>0 else str(0))+" and the behavior received temp value "+str(ts.sensors['temp'])+" at time after midnight "+str(t%day_seconds)+" so new LED setting should be "+str(correct[i])+". You sent "+str(ta.actions[2]['led'])+"."
            assert ta.actions and ta.actions[2]['led'] == correct[i], s

        
def checkRaiseTempBehaviorDisable(rtb):
    temp = [20, 25, 26, 31, 30, 29, 28, 27, 26, 25, 24, 23, 22, 21, 20, 19, 18,
            17, 16, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
            30, 31, 32, 31, 30, 29, 28, 27, 26, 25, 24, 23, 22, 21]
    correct = [200, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 200, 200, 200, 200,
               200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 0,
               0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 200]
    t = 0
    dtime = 1800

    ts = TestSensors()
    ta = TestActuators()
    rtb.setSensors(ts)
    rtb.setActuators(ta)

    assert(ta.actions == None), "Unexpected action set"
    ts.setSense({"unix_time":0, "midnight_time":0, "temp": temp[0]})

    for j in range(3):
        rtb.start()
        assert(ta.actions and ta.actions[2] == {"led":0}), "LEDs not turned off initially"

        for i in range(20):
            t = dtime*(i+(j*48))
            ts.setSense({"unix_time":t,
                         "midnight_time":t%day_seconds,
                         "temp": temp[i]})
            rtb.doStep()
            s = "RaiseTemp Error: LED settings not correct. LEDs were set to "+(str(correct[i-1]) if i>0 else str(0))+" and the behavior received temp value "+str(ts.sensors['temp'])+" at time after midnight "+str(t%day_seconds)+" so new LED setting should be "+str(correct[i])+". You sent "+str(ta.actions[2]['led'])+". Maybe you are not handing disable/enable correctly?"
            assert ta.actions and ta.actions[2]['led'] == correct[i], s

        rtb.disable()

def checkLowerHumidBehavior3Days(lhb):
    humid = [59, 60, 61, 63, 65, 67, 69, 71, 73, 75, 77, 79, 81, 83, 85, 87,
             89, 91, 93, 95, 94, 92, 90, 88, 86, 84, 82, 80, 78, 76, 74, 72,
             70, 68, 66, 75, 80, 85, 90, 91, 92, 93, 90, 89, 85, 80, 75, 70]
    correct = [False, False, False, False, False, False, False, False, False,
               False, False, False, False, False, False, False, False, True,
               True, True, True, True, True, True, True, True, True, False,
               False, False, False, False, False, False, False, False, False,
               False, True, True, True, True, True, True, True, False, False, False]
    t = 0
    dtime = 1800

    ts = TestSensors()
    ta = TestActuators()
    lhb.setSensors(ts)
    lhb.setActuators(ta)

    assert(ta.actions == None), "Unexpected action set"
    ts.setSense({"unix_time":0, "midnight_time":0, "humid": humid[0]})
    lhb.start()
    assert(ta.actions and ta.actions[2] == {"fan":False}), "Fan not turned off initially"
    
    for j in range(3):
        for i in range(48):
            t = dtime*(i+(j*48))
            ts.setSense({"unix_time":t,
                         "midnight_time":t%day_seconds,
                         "humid": humid[i]})
            lhb.doStep()

            s = "LowerHumid Error: Fan settings not correct. Fans were set to "+(str(correct[i-1]) if i>0 else str(False))+" and the behavior received humid value "+str(ts.sensors['humid'])+" at time after midnight "+str(t%day_seconds)+" so new Fan setting should be "+str(correct[i])+". You sent "+str(ta.actions[2]['fan'])+"."
            assert ta.actions and ta.actions[2]['fan'] == correct[i], s

        
def checkLowerHumidBehaviorDisable(lhb):
    humid = [59, 60, 61, 63, 65, 67, 69, 71, 73, 75, 77, 79, 81, 83, 85, 87,
             89, 91, 93, 95, 94, 92, 90, 88, 86, 84, 82, 80, 78, 76, 74, 72,
             70, 68, 66, 75, 80, 85, 90, 91, 92, 93, 90, 89, 85, 80, 75, 70]
    correct = [False, False, False, False, False, False, False, False, False,
               False, False, False, False, False, False, False, False, True,
               True, True, True, True, True, True, True, True, True, False,
               False, False, False, False, False, False, False, False, False,
               False, True, True, True, True, True, True, True, False, False, False]

    t = 0
    dtime = 1800

    ts = TestSensors()
    ta = TestActuators()
    lhb.setSensors(ts)
    lhb.setActuators(ta)

    assert(ta.actions == None), "Unexpected action set"
    ts.setSense({"unix_time":0, "midnight_time":0, "humid": humid[0]})

    for j in range(3):
        lhb.start()
        assert(ta.actions and ta.actions[2] == {"fan":False}), "Fan not turned off initially"

        for i in range(42):
            t = dtime*(i+(j*48))
            ts.setSense({"unix_time":t,
                         "midnight_time":t%day_seconds,
                         "humid": humid[i]})
            lhb.doStep()

            s = "LowerHumid Error: Fan settings not correct. Fan were set to "+(str(correct[i-1]) if i>0 else str(False))+" and the behavior received humid value "+str(ts.sensors['humid'])+" at time after midnight "+str(t%day_seconds)+" so new Fan setting should be "+str(correct[i])+". You sent "+str(ta.actions[2]['fan'])+". Maybe you are not handing disable/enable correctly?"
            assert ta.actions and ta.actions[2]['fan'] == correct[i], s

        lhb.disable()


def checkLowerSMoistBehavior3Days(lsb):
    smoist = [450, 460, 470, 480, 490, 500, 510, 520, 530, 540, 550, 560, 570,
              580, 590, 600, 610, 620, 630, 640, 650, 660, 670, 680, 690, 680,
              670, 660, 650, 640, 630, 620, 610, 600, 590, 580, 570, 560, 550,
              600, 650, 700, 660, 640, 620, 600, 550, 610]
    correct = [False, False, False, False, False, False, False, False, False,
               False, False, False, False, False, False, False, False, False,
               False, False, True, True, True, True, True, True, True, True,
               True, True, True, True, True, False, False, False, False, False,
               False, False, True, True, True, True, True, False, False, False]
    
    t = 0
    dtime = 1800

    ts = TestSensors()
    ta = TestActuators()
    lsb.setSensors(ts)
    lsb.setActuators(ta)

    assert(ta.actions == None), "Unexpected action set"
    ts.setSense({"unix_time":0, "midnight_time":0, "smoist": smoist[0]})
    lsb.start()
    assert(ta.actions and ta.actions[2] == {"fan":False}), "Fan not turned off initially"
    
    for j in range(3):
        for i in range(48):
            t = dtime*(i+(j*48))
            ts.setSense({"unix_time":t,
                         "midnight_time":t%day_seconds,
                         "smoist": smoist[i]})
            lsb.doStep()
            s = "LowerSMoist Error: Fan settings not correct. Fans were set to "+(str(correct[i-1]) if i>0 else str(False))+" and the behavior received smoist value "+str(ts.sensors['smoist'])+" at time after midnight "+str(t%day_seconds)+" so new Fan setting should be "+str(correct[i])+". You sent "+str(ta.actions[2]['fan'])+"."
            assert ta.actions and ta.actions[2]['fan'] == correct[i], s

        
def checkLowerSMoistBehaviorDisable(lsb):
    smoist = [450, 460, 470, 480, 490, 500, 510, 520, 530, 540, 550, 560, 570,
              580, 590, 600, 610, 620, 630, 640, 650, 660, 670, 680, 690, 680,
              670, 660, 650, 640, 630, 620, 610, 600, 590, 580, 570, 560, 550,
              600, 650, 700, 660, 640, 620, 600, 550, 610]
    correct = [False, False, False, False, False, False, False, False, False,
               False, False, False, False, False, False, False, False, False,
               False, False, True, True, True, True, True, True, True, True,
               True, True, True, True, True, False, False, False, False, False,
               False, False, True, True, True, True, True, False, False, False]

    t = 0
    dtime = 1800

    ts = TestSensors()
    ta = TestActuators()
    lsb.setSensors(ts)
    lsb.setActuators(ta)

    assert(ta.actions == None), "Unexpected action set"
    ts.setSense({"unix_time":0, "midnight_time":0, "smoist": smoist[0]})

    for j in range(3):
        lsb.start()
        assert(ta.actions and ta.actions[2] == {"fan":False}), "Fan not turned off initially"

        for i in range(42):
            t = dtime*(i+(j*48))
            ts.setSense({"unix_time":t,
                         "midnight_time":t%day_seconds,
                         "smoist": smoist[i]})
            lsb.doStep()
            s = "LowerSMoist Error: Fan settings not correct. Fan were set to "+(str(correct[i-1]) if i>0 else str(False))+" and the behavior received smoist value "+str(ts.sensors['smoist'])+" at time after midnight "+str(t%day_seconds)+" so new Fan setting should be "+str(correct[i])+". You sent "+str(ta.actions[2]['fan'])+". Maybe you are not handing disable/enable correctly?"
            assert ta.actions and ta.actions[2]['fan'] == correct[i], s

        lsb.disable()


def checkLowerSMoistBehavior3Days(lsb):
    smoist = [450, 460, 470, 480, 490, 500, 510, 520, 530, 540, 550, 560, 570,
              580, 590, 600, 610, 620, 630, 640, 650, 660, 670, 680, 690, 680,
              670, 660, 650, 640, 630, 620, 610, 600, 590, 580, 570, 560, 550,
              600, 650, 700, 660, 640, 620, 600, 550, 610]
    correct = [False, False, False, False, False, False, False, False, False,
               False, False, False, False, False, False, False, False, False,
               False, False, True, True, True, True, True, True, True, True,
               True, True, True, True, True, False, False, False, False, False,
               False, False, True, True, True, True, True, False, False, False]
    
    t = 0
    dtime = 1800

    ts = TestSensors()
    ta = TestActuators()
    lsb.setSensors(ts)
    lsb.setActuators(ta)

    assert(ta.actions == None), "Unexpected action set"
    ts.setSense({"unix_time":0, "midnight_time":0, "smoist": smoist[0]})
    lsb.start()
    assert(ta.actions and ta.actions[2] == {"fan":False}), "Fan not turned off initially"
    
    for j in range(3):
        for i in range(48):
            t = dtime*(i+(j*48))
            ts.setSense({"unix_time":t,
                         "midnight_time":t%day_seconds,
                         "smoist": smoist[i]})
            lsb.doStep()
            s = "LowerSMoist Error: Fan settings not correct. Fans were set to "+(str(correct[i-1]) if i>0 else str(False))+" and the behavior received smoist value "+str(ts.sensors['smoist'])+" at time after midnight "+str(t%day_seconds)+" so new Fan setting should be "+str(correct[i])+". You sent "+str(ta.actions[2]['fan'])+"."
            assert ta.actions and ta.actions[2]['fan'] == correct[i], s

def setRaiseSMoistSensorData(ts, datum):
    ts.setSense({"unix_time":datum[0],
                 "midnight_time":datum[0]%day_seconds,
                 "level" : datum[1],
                 "smoist": datum[2],
                 "weight": datum[3]})

def checkRaiseSMoistBehavior4Days(rsb):
    # Time, wlevel, smoist, weight, pump
    d2 = day_seconds; d3 = 2*day_seconds; d4 = 3*day_seconds
    sdata = [
        # Day 1 - water twice (30 ml each)
        [30600, 150, 450, 1000, False], [30602, 150, 450, 1000, False],
        [30605, 150, 450, 1000, False], [30610, 150, 450, 1000, False],
        [30611, 149, 450, 1000, True],  [30616, 149, 460, 1015, True],
        [30621, 148, 470, 1025, False], [30625, 148, 475, 1030, False],
        [30628, 148, 480, 1030, False], [30630, 148, 490, 1030, False],
        [30635, 148, 500, 1030, False], [30638, 148, 500, 1030, False],
        [30640, 148, 500, 1030, False], [30641, 148, 500, 1030, False],

        [30642, 148, 500, 1030, True],  [30647, 147, 510, 1045, True],
        [30652, 146, 520, 1055, False], [30656, 146, 540, 1060, False],
        [30659, 147, 550, 1060, False], [30660, 147, 560, 1060, False],
        [30665, 147, 560, 1060, False], [30668, 147, 560, 1060, False],
        [30670, 147, 560, 1060, False], [30672, 147, 560, 1060, False],

        [30673, 147, 560, 1060, False], [30680, 147, 560, 1060, False],
        [d2-1, 147, 560, 1060, False], # End of day 1

        # Day 2 - don't water - moist enough
        [d2, 147, 560, 1060, False],       [d2+1, 147, 560, 1060, False],
        [d2+2, 147, 560, 1060, False],     [d2+3, 147, 560, 1060, False],
        [d2+4, 147, 560, 1060, False],     [d2+5, 147, 560, 1060, False],
        [d2+30600, 147, 560, 1060, False], [d2+30602, 147, 560, 1060, False],
        [d2+30605, 147, 560, 1060, False], [d2+30610, 147, 560, 1060, False],
        [d2+30611, 147, 560, 1060, False], [d2+30616, 147, 560, 1060, False],
        [d2+30621, 147, 560, 1025, False], [d2+30625, 147, 555, 1055, False],
        [d2+30628, 147, 555, 1055, False], [d2+30630, 147, 550, 1050, False],
        [d2+30635, 147, 550, 1050, False], [d2+30638, 147, 550, 1050, False],
        [d2+30640, 147, 550, 1050, False], [d2+30641, 147, 550, 1050, False],
        [d3-1, 147, 550, 1050, False], # End of day 2

        # Day 3 - water once (50 ml), disable before finished pumping
        [d3, 147, 450, 1050, False],       [d3+1, 147, 450, 1050, False],
        [d3+2, 147, 450, 1050, False],     [d3+3, 147, 450, 1050, False],
        [d3+4, 147, 450, 1050, False],     [d3+5, 147, 450, 1050, False],
        [d4-10, 147, 450, 1050, False], [d4-6, 147, 450, 1050, True],
        [d4-5, 147, 450, 1050, True], [d4-4, 147, 450, 1050, True],
        [d4-3, 147, 450, 1050, True], [d3-2, 147, 450, 1050, True],
        [d4-1, 147, 450, 1050, False], # End of day 3, halt while pumping

        # Day 4 - don't water (not enough water in reservoir)
        [d4, 20, 450, 1050, False],   [d4+1, 20, 450, 1050, False],
        [d4+2, 20, 450, 1050, False], [d4+3, 20, 450, 1050, False],
        [d4+4, 20, 450, 1050, False], [d4+5, 20, 450, 1050, False],
        [d4+30600, 20, 450, 1050, False], [d4+30601, 20, 450, 1050, False]
        ]

    ts = TestSensors()
    ta = TestActuators()
    rsb.setSensors(ts)
    rsb.setActuators(ta)

    assert(ta.actions == None), "Unexpected action set"
    last_datum = sdata[0]
    last_pump = last_datum[4]
    last_weight = last_datum[3]
    setRaiseSMoistSensorData(ts, last_datum)
    rsb.start()
    disabled = False
    assert(ta.actions and ta.actions[2] == {'wpump':False}), "Pump not turned off initially"

    for datum in sdata[1:]:
        #print("DATUM:", datum)
        setRaiseSMoistSensorData(ts, datum)
        rsb.doStep()

        time, wlevel, smoist, weight, pump = datum
        # Reset each day
        if ((time+1)%day_seconds == 0): rsb.disable(); disabled = True
        elif (time%day_seconds == 0): rsb.start(); disabled = False

        if (time%day_seconds < last_datum[1]%day_seconds):
            last_weight = weight
            #print("Start weight reset to %d at time %d after midnight" %(weight, time%day_seconds))

        s = "RaiseSMoist Pump settings not correct.  "
        if (disabled):
            s += "Pump not turned off when behavior disabled"
        elif (pump and not last_pump):
            s += ("Pump not turned on even though moisture is %d and watered %.2f this day"
                  %(smoist, (last_weight - weight)))
        elif (not pump and last_pump):
            s += "Pump not turned off even though more than 10 seconds have passed"
        elif (not pump and not last_pump):
            s += "Pump turned on unexpectedly"
        elif  (pump and last_pump):
            s += "Pump turned off unexpectedly"
        s += "  at time %d after midnight" %(time%day_seconds)

        assert ta.actions and ta.actions[2]['wpump'] == pump, s
        last_datum = datum

