import argparse
from math import floor, ceil

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--part', default=-1, type=int,
                    help='Which part to test (defaults to all)')
parser.add_argument('-t', '--test', default=-1, type=int,
                    help='Which test to use (defaults to all)')
parser.add_argument('-k', '--keep', action='store_true',
                    help='Keep log file at end of run (deafults to False)')
args = parser.parse_args()

if (args.part in [-1, 1]):
    from coffee_maker import *
    import autograder_coffee_maker
    print("Part 1: Coffee Maker")
    autograder_coffee_maker.parse_coffee_test(args.test, args.keep)
    print()

def do_test(test_num, test_name, behavior_fn, test1_fn, test2_fn=None):
    test_points = 5 # Number of points per test
    print("Test %d: Checking %s behavior" %(test_num, test_name))
    points1 = 0
    try:
        test1_fn(behavior_fn())
        points1 = test_points
    except AssertionError as msg: print("Error: ", msg)
    if (not test2_fn):
        points = points1
    else:
        points2 = 0
        try:
            test2_fn(behavior_fn())
            points2 = test_points
        except AssertionError as msg: print("Error: ", msg)
        points = ceil(points1/2.0) + floor(points2/2.0)
    print("%s behavior: %d/%d\n" %(test_name, points, test_points))
    return points, test_points

if (args.part in [-1, 2]):
    from autograder_greenhouse import *
    import greenhouse_behaviors as gb
    import ping_behavior as ping
    #test_points = 5 # Number of points per test
    total_points = possible_points = 0
    print("Part 2: Greenhouse")
    if (args.test in [-1, 1]): 
        points, test_points = do_test(1, "Light", gb.Light,
                                      checkLightBehavior3Days,
                                      checkLightBehaviorDisable)
        total_points += points; possible_points += test_points

    if (args.test in [-1, 2]): 
        points, test_points = do_test(2, "LowerTemp", gb.LowerTemp,
                                      checkLowerTempBehavior3Days,
                                      checkLowerTempBehaviorDisable)
        total_points += points; possible_points += test_points

    if (args.test in [-1, 3]): 
        points, test_points = do_test(3, "LowerHumid", gb.LowerHumid,
                                      checkLowerHumidBehavior3Days,
                                      checkLowerHumidBehaviorDisable)
        total_points += points; possible_points += test_points

    if (args.test in [-1, 4]): 
        points, test_points = do_test(4, "RaiseSMoist", gb.RaiseSMoist,
                                      checkRaiseSMoistBehavior4Days)
        total_points += points; possible_points += test_points

    if (args.test in [-1, 5]): 
        points, test_points = do_test(5, "LowerSMoist", gb.LowerSMoist,
                                      checkLowerSMoistBehavior3Days,
                                      checkLowerSMoistBehaviorDisable)
        total_points += points; possible_points += test_points

    if (args.test in [-1, 6]): 
        points, test_points = do_test(6, "RaiseTemp", gb.RaiseTemp,
                                      checkRaiseTempBehavior3Days,
                                      checkRaiseTempBehaviorDisable)
        total_points += points; possible_points += test_points

    if (args.test in [-1, 7]): 
        points, test_points = do_test(7, "Ping", ping.Ping, checkPingBehavior)
        total_points += points; possible_points += test_points

    print("Overall score: %d/%d" %(total_points, possible_points))
