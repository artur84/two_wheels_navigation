#!/usr/bin/env python
import rospy
from geometry_msgs.msg import Twist



class VelRemap():
    #This node recieves a Twist message from the cmd_vel_input topic and publishes to cmd_vel a
    # value scaled by some factor to adjust the velocity published by the nav2d operator to work with our simulated robot.
    def __init__(self):
        """ Parameters
        """

        rospy.logdebug("Setting publishers...")
        self.pub_cmd_vel = rospy.Publisher('cmd_vel', Twist, queue_size=10)
        ############################### SUBSCRIBERS #####################################
        rospy.Subscriber("cmd_vel_input", Twist, self.cmd_vel_cb)
        ############ CONSTANTS ################
        r=rospy.Rate(10)
        self.cmd_vel_msg=Twist()
        while not rospy.is_shutdown():
            r.sleep()

    def cmd_vel_cb(self, msg):
        ## This function receives a Twist and copies the linear and angular velocities
        self.cmd_vel_msg.angular.z=msg.angular.z
        self.cmd_vel_msg.linear.x=msg.linear.x*0.5
        #limit the maximum values
        if self.cmd_vel_msg.angular.z>0.4:
            self.cmd_vel_msg.angular.z=0.4
        if self.cmd_vel_msg.linear.x>0.6:
            self.cmd_vel_msg.linear.x=0.6

        self.pub_cmd_vel.publish(self.cmd_vel_msg)



    def cleanup(self):
        #This function is called just before finishing the node
        # You can use it to clean things up before leaving
        # Example: stop the robot before finishing a node.
        pass


############################### MAIN PROGRAM ####################################
if __name__ == "__main__":
    rospy.init_node("vel_remap", anonymous=True)
    try:
	    VelRemap()
    except:
        rospy.logfatal("vel_remap died")
