import os, sys, logging, time
from coffee_maker import *
from datetime import datetime
from terrabot_utils import time_since_midnight

global_time = 0

def sense_act(cm, sensordata={}, dt=1):
    global global_time
    global_time += dt
    sensordata['unix_time'] = global_time
    sensordata['midnight_time'] = time_since_midnight(global_time)
    cm.sense(sensordata)
    cm.act()

def wait_for_dispensing(cm, duration):
    for i in range(duration):
        #time.sleep(1)
        sense_act(cm)
        try:
            if (cm.action == "DONE DISPENSING"): return True
        except AttributeError: pass
    return False

def message_time(line):
    return datetime.strptime(line[line.find("s:")+2:line.find(",")],
                             '%Y-%m-%d %H:%M:%S.%f')

def test_smallsize_easy_transitions():
    cm = CoffeeMaker()
    sense_act(cm, {"smallbuttonpressed":True})
    sense_act(cm, {"podpresent":True})
    sense_act(cm, {"startbuttonpressed": True})
    sense_act(cm, {"watertemp": 180})
    if (not wait_for_dispensing(cm, 10)): return # Failed
    sense_act(cm, {"podpresent":False, "smallbuttonpressed":False})
    # Should be back to empty state; should raise an error if not

def test_medsize_easy_transitions():
    cm = CoffeeMaker()
    sense_act(cm, {"medbuttonpressed":True})
    sense_act(cm, {"podpresent":True})
    sense_act(cm, {"startbuttonpressed": True})
    sense_act(cm, {"watertemp": 180})
    if (not wait_for_dispensing(cm, 15)): return # Failed
    sense_act(cm, {"podpresent":False, "medbuttonpressed":False})
    # Should be back to empty state; should raise an error if not

def test_largesize_easy_transitions():
    cm = CoffeeMaker()
    sense_act(cm, {"largebuttonpressed":True})
    sense_act(cm, {"podpresent":True})
    sense_act(cm, {"startbuttonpressed": True})
    sense_act(cm, {"watertemp": 180})
    if (not wait_for_dispensing(cm, 20)): return # Failed
    sense_act(cm, {"podpresent":False, "largebuttonpressed":False})
    # Should be back to empty state; should raise an error if not

def test_smallsize_removepod():
    cm = CoffeeMaker()
    sense_act(cm, {"smallbuttonpressed":True})
    sense_act(cm, {"podpresent":True})
    sense_act(cm, {"podpresent":False})
    sense_act(cm, {"startbuttonpressed": True})
    sense_act(cm, {"watertemp": 180})
    wait_for_dispensing(cm, 10)
    sense_act(cm, {"podpresent":False, "smallbuttonpressed":False})
    #should NOT be back to empty state
    #should NOT have brewed


def test_smallsize_podfirst():
    cm = CoffeeMaker()
    sense_act(cm, {"podpresent":True})
    sense_act(cm, {"smallbuttonpressed":True})
    sense_act(cm, {"startbuttonpressed": True})
    sense_act(cm, {"watertemp": 180})
    if (not wait_for_dispensing(cm, 10)): return # Failed
    sense_act(cm, {"podpresent":False, "smallbuttonpressed":False})
    #should have brewed

def test_nowater():
    cm = CoffeeMaker()
    sense_act(cm, {"podpresent":True})
    sense_act(cm, {"smallbuttonpressed":True})
    sense_act(cm, {"startbuttonpressed": True})
    wait_for_dispensing(cm, 10)
    sense_act(cm, {"podpresent":False, "smallbuttonpressed":False})
    #should NOT be back to empty state
    #should NOT have brewed

def test_waitwater():
    cm = CoffeeMaker()
    sense_act(cm, {"podpresent":True})
    sense_act(cm, {"smallbuttonpressed":True})
    sense_act(cm, {"startbuttonpressed": True})
    for i in range(10):
        #time.sleep(.2)
        sense_act(cm, {"watertemp": 60+(i*10)}, 0.2)
    sense_act(cm, {"watertemp": 180})
    if (not wait_for_dispensing(cm, 10)): return # Failed
    sense_act(cm, {"podpresent":False, "smallbuttonpressed":False})
    #should be at empty


def test_switchsize():
    cm = CoffeeMaker()
    sense_act(cm, {"smallbuttonpressed":True})
    sense_act(cm, {"podpresent":True})
    sense_act(cm, {"smallbuttonpressed":False,"medbuttonpressed":True})
    sense_act(cm, {"startbuttonpressed": True})
    sense_act(cm, {"watertemp": 180})
    if (not wait_for_dispensing(cm, 15)): return # Failed
    sense_act(cm, {"podpresent":False, "smallbuttonpressed":False})
    #should be back in empty

def test_nosize():
    cm = CoffeeMaker()
    sense_act(cm, {"podpresent":True})
    sense_act(cm, {"startbuttonpressed": True})
    sense_act(cm, {"watertemp": 180})
    wait_for_dispensing(cm, 10)
    sense_act(cm, {"podpresent":False, "smallbuttonpressed":False})
    #should be back in empty

def test_smallsize_nopod():
    cm = CoffeeMaker()
    sense_act(cm, {"smallbuttonpressed":True})
    sense_act(cm, {"startbuttonpressed": True})
    sense_act(cm, {"watertemp": 180})
    wait_for_dispensing(cm, 10)
    sense_act(cm, {"podpresent":False, "smallbuttonpressed":False})
    #should NOT be back to empty state
    #should NOT have brewed

def test_smallsize_nostart():
    cm = CoffeeMaker()
    sense_act(cm, {"smallbuttonpressed":True})
    sense_act(cm, {"podpresent":True})
    sense_act(cm, {"watertemp": 180})
    wait_for_dispensing(cm, 10)
    sense_act(cm, {"podpresent":False, "smallbuttonpressed":False})
    #should NOT be back to empty state
    #should NOT have brewed


def do_test(logger, test_num, short_name, long_name, test_fn, choice):
    if (choice <= 0 or choice == test_num):
        logger.info("START %s" %short_name)
        print("Running Test %d: %s" %(test_num, long_name))
        test_fn()
        logger.info("END %s" %short_name)

def coffeetests(testnum):
    global global_time
    file = 'output-cm'+str(datetime.now().strftime("%Y-%m-%d %H-%M-%S"))+'.log'
    global_time = datetime.now().timestamp()
    logging.basicConfig(filename=file, level=logging.INFO)
    testlogger = logging.getLogger('tests')
    testlogger.setLevel(logging.INFO)
    do_test(testlogger, 1, "SMALL SIZE", "Small Size Coffee Brew Time",
            test_smallsize_easy_transitions, testnum)
    do_test(testlogger, 2, "MED SIZE", "Medium Size Coffee Brew Time",
            test_medsize_easy_transitions, testnum)
    do_test(testlogger, 3, "LARGE SIZE", "Large Size Coffee Brew Time",
            test_largesize_easy_transitions, testnum)
    do_test(testlogger, 4, "NO START", "No Start Button",
            test_smallsize_nostart, testnum)
    do_test(testlogger, 5, "REMOVE POD", "Remove Pod",
            test_smallsize_removepod, testnum)
    do_test(testlogger, 6, "POD FIRST", "Pod First",
            test_smallsize_podfirst, testnum)
    do_test(testlogger, 7, "NO POD", "No Pod", test_smallsize_nopod, testnum)
    do_test(testlogger, 8, "NO SIZE","No Size Button", test_nosize, testnum)
    do_test(testlogger, 9, "SWITCH SIZE", "Switch Size Brew Time",
            test_switchsize, testnum)
    do_test(testlogger, 10, "WAIT WATER", "Wait Water Temp Time",
            test_waitwater, testnum)
    do_test(testlogger, 11, "NO HEAT WATER", "No Water Temp",
            test_nowater, testnum)
    return file

def expected(action, action_name, test):
    if (action): return 1
    else:
        print("Did not find %s action in test %s when one is expected"
              %(action_name, test))
        return 0

def not_expected(action, action_name, test):
    if (not action): return 1
    else: 
        print("Found %s action in test %s when not expected" %(action_name, test))
        return 0

def correct_wait(start_time, end_time, wait_time,
                 start_action, end_action, test):
    if (start_time and end_time and wait_time):
        dt = int((end_time-start_time).total_seconds())
        if (dt == wait_time): return 1
        else:
            print(("Found %s and %s actions in test %s, "+
                   "but incorrect time elapsed (was %s, expected %s)")
                  %(start_action, end_action, test, dt, wait_time))
            return 0
    else: return 1

def parse_coffee_test(testnum, keep_file):
    total_points = possible_points = 0
    test_points = 3 # Number of points per test
    alltests = ["SMALL SIZE", "MED SIZE", "LARGE SIZE", "NO START",
                "REMOVE POD", "POD FIRST", "NO POD", "NO SIZE", "SWITCH SIZE",
                "WAIT WATER", "NO HEAT WATER"]
    if testnum > 0 and testnum <= len(alltests):
        tests = [alltests[testnum-1]]
    else:
        tests = alltests
    file = coffeetests(testnum)
    # Key: should_dispense?, dispense_time, should_heat?, wait_time
    actions = {"SMALL SIZE":    (True,  5,    True,  6),
               "MED SIZE":      (True,  10,   True,  11),
               "LARGE SIZE":    (True,  15,   True,  16),
               "NO START":      (False, None, False, None),
               "REMOVE POD":    (False, None, False, None),
               "POD FIRST":     (True,  5,    True,  6),
               "NO POD":        (False, None, False, None),
               "NO SIZE":       (False, None, False, None),
               "SWITCH SIZE":   (True,  10,   True,  11),
               "WAIT WATER":    (True,  5,    True,  8),
               "NO HEAT WATER": (False, None, True,  None)}
    for test in tests:
        if testnum <= 0:
            print("Grading Test", tests.index(test)+1, "Name:", test)
        else:
            print("Grading Test", testnum, "Name:",test)
        f = open(file,"r")
        log = f.read()
        lines = log.split("\n")
        i=0
        foundtest = False
        passedtest = True
        while i < len(lines):
            if "START "+test in lines[i]:
                startheating = None
                startdispensing = None
                enddispensing = None
                foundtest = True
                points = 0
                i+=1
                while "END "+test not in lines[i]:
                    if not "actions" in lines[i]:
                        pass
                    elif "START HEATING" in lines[i]:
                        startheating = message_time(lines[i])
                    elif "START DISPENSING" in lines[i]:
                        startdispensing = message_time(lines[i])
                    elif "DONE DISPENSING" in lines[i]:
                        enddispensing = message_time(lines[i])
                    i += 1
                should_heat = actions[test][2]
                wait_time = actions[test][3]
                should_dispense = actions[test][0]
                dispense_time = actions[test][1]
                if (not should_heat):
                    points += not_expected(startheating, "START HEATING", test)
                    points += not_expected(startdispensing,
                                           "START DISPENSING", test)
                    points += not_expected(enddispensing,
                                           "END DISPENSING", test)
                else: # Should heat
                    points += expected(startheating, "START HEATING", test)
                    if (not should_dispense):
                        points += not_expected(startdispensing,
                                               "START DISPENSING", test)
                        points += not_expected(enddispensing,
                                               "END DISPENSING", test)
                    else: # Should dispense
                        points += expected(startdispensing, "START DISPENSING", test)
                        # For enddispensing, have to get timing right as well
                        points += (expected(enddispensing, "END DISPENSING", test) and
                                   correct_wait(startdispensing, enddispensing,
                                                dispense_time, "START DISPENSING",
                                                "END DISPENSING", test) and
                                   correct_wait(startheating, enddispensing, wait_time,
                                                "START HEATING", "END DISPENSING", test))
            i=i+1
        f.close()
        if not foundtest:
            print("Test did not run. Did the FSM crash?")
        else:
            total_points += points
            possible_points += test_points
            print("Passed Test: %s %d/%d" %(test, points, test_points))

    print("Overall score: %d/%d" %(total_points, possible_points))
    if (not keep_file): os.remove(file)
    return

'''
if len(sys.argv) == 1 or "1" in sys.argv[1]:
    from coffeemaker import *
    print("Part 1: Coffee Maker")
    parsecoffeetest(coffeetests())
'''
