#!/usr/bin/env python
#This program makes the join1 of the two wheels robot move.
import rospy
from std_msgs.msg import Float64  
import numpy as np


class ArmMover():
    #This node recieves a Twist message from the cmd_vel topic and publishes odometry
    def __init__(self):
        ###******* INIT PUBLISHERS *******###
        self.pub_joint1 = rospy.Publisher('/two_wheels_robot/joint1_position_controller/command', Float64, queue_size=10)
        
        ############ CONSTANTS ################
        self.angle1 = 0.0  #The desired angle for joint 1
        print "Node initialized"
        r=rospy.Rate(10) #The following while loop will be executed at a 10Hz rate
        while not rospy.is_shutdown():
            self.pub_joint1.publish(self.angle1)
            self.angle1=self.angle1+0.05
            if self.angle1 > np.pi:
                self.angle1=0
            r.sleep()  

############################### MAIN PROGRAM ####################################
if __name__ == "__main__":
    rospy.init_node("arm_mover", anonymous=True)
    try:
	    ArmMover()
    except:
        rospy.logfatal("arm_mover died")
