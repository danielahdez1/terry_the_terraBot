import rospy
import argparse
from std_msgs.msg import Int32, Bool
from ros_hardware import ROSSensors, ROSActuators

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--part', default=-1, type=int,
                    help='Which part to test (defaults to all)')
args = parser.parse_args()

def fan_callback(data): actuator_callbacks['fan'] = data.data
def pump_callback(data): actuator_callbacks['wpump'] = data.data
def led_callback(data): actuator_callbacks['led'] = data.data

rospy.set_param('use_sim_time', True)
rospy.init_node('test_ros_hardware_agent', anonymous = True)
sensors = ROSSensors()
actuators = ROSActuators()
acts = {'fan' : False, 'wpump' : False, 'led' : 10}
actuator_callbacks = acts.copy()
rospy.Subscriber('fan_input', Bool, fan_callback)
rospy.Subscriber('wpump_input', Bool, pump_callback)
rospy.Subscriber('led_input', Int32, led_callback)

def error(msg):
    raise Exception(msg)

def check_for_single_sensor_error(sensor, raw, value):
    #print(sensor, raw, value)
    if (raw == 0): error("%s_raw value is zero (should be positive)" %sensor)
    if (value != raw):
        error("%s (%s) not equal to %s_raw (%s)" %(sensor, value, sensor, raw))

def check_for_dual_sensor_error(sensor, raw, value):
    if (raw[0] == 0 or raw[1] == 0):
        error("%s_raw values are zero (should be positive)" %sensor)
    if (value != sum(raw)/2):
        error("%s (%s) not average of %s_raw: %s" %(sensor, value, sensor, raw))

def check_for_actuator_error(actuator, actuators, acts):
    actual = actuators.actuator_state[actuator]
    desired = acts[actuator]
    received = actuator_callbacks[actuator]
    if (actual != desired):
        error("%s: actuator_state value (%s) not same as desired value (%s)"
              %(actuator, actual, desired))
    if (received != desired):
        error("%s: TerraBot did not receive the desired value (%s)"
              %(actuator, desired))

actuators.actuator_state["led"] = acts["led"]
actuators.actuators['led'].publish(acts["led"])

max_iterations = 3 if args.part == 1 else 6

# Give the sensors a chance to get loaded up
count = 0
while not rospy.core.is_shutdown() and count < 5:
    sensors.doSense()
    rospy.sleep(1)
    count += 1

count = 1
pump_act = fan_act = led_act = False
while not rospy.core.is_shutdown() and count <= max_iterations:
    print("Iteration %d" %count)
    if (args.part in [-1, 1]):
        sensors.doSense()
        check_for_dual_sensor_error("light_level", sensors.light_level_raw,
                                    sensors.light_level)
        check_for_dual_sensor_error("temperature", sensors.temperature_raw,
                                    sensors.temperature)
        check_for_dual_sensor_error("humidity", sensors.humidity_raw,
                                    sensors.humidity)
        check_for_dual_sensor_error("weight", sensors.weight_raw,
                                    sensors.weight)
        check_for_dual_sensor_error("moisture", sensors.moisture_raw,
                                    sensors.moisture)
        check_for_single_sensor_error("wlevel", sensors.wlevel_raw,
                                      sensors.wlevel)

    if (args.part in [-1, 2]):
        acts["wpump"] = not acts["wpump"]; pump_act = True
        if (count %2 == 0): acts["led"] = 200-acts["led"]; led_act = True
        if (count %3 == 0): acts["fan"] = not acts["fan"]; fan_act = True
        actuators.doActions(('test', 0, acts))
    rospy.sleep(2)

    if pump_act: check_for_actuator_error("wpump", actuators, acts)
    if fan_act: check_for_actuator_error("fan", actuators, acts)
    if led_act: check_for_actuator_error("led", actuators, acts)
    pump_act = fan_act = led_act = False

    count += 1
