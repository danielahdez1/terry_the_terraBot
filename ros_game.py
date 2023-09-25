# Set up remote ROS communications:
# For VirtualBox: In the GUI, go to Settings -> Network, and set
#  "attached to" to be "Bridge Adapter"
# FOR UTM: In the GUI, go to Devices -> Network -> Network Mode, set to
#  "Bridged (Advanced)" and save the configureation
# In the VM, type "ip a | grep inet"
#   One of the lines will have your IP address (mine starts 172)
#   enter: export ROS_IP=<IP address>
#   enter: export ROS_MASTER_URI=http://172.26.39.40:11311

import rospy
import os, sys, select, random
from std_msgs.msg import String

rospy.init_node("ROS_GAME", anonymous = True)

# Create a publisher for the "response" message (topic), whose format is String
# BEGIN STUDENT CODE
# END STUDENT CODE

# Create a subscriber for the "word" message, whose format is String, and
#   has a callback such that when a "word" message is received, it sends
#   a "response" message consisting of a single string that includes
#   your Andrew ID and the received word, separated by a space
# BEGIN STUDENT CODE
# END STUDENT CODE

def check_for_input():
    if sys.stdin in select.select([sys.stdin],[],[],0)[0]:
        input = sys.stdin.readline()
        if input[0] == 'q':
            quit()
        else:
            print("Usage: q (quit)")

while not rospy.core.is_shutdown():
    rospy.sleep(0.5)
    check_for_input()
