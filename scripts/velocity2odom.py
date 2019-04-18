#!/usr/bin/env python
import rospy
from std_msgs.msg import Int32  
from geometry_msgs.msg import Twist
from geometry_msgs.msg import TransformStamped
from geometry_msgs.msg import Quaternion
from nav_msgs.msg import Odometry
import numpy as np
import rospy
from copy import deepcopy
import tf
import math
#This class will receive a number and an increment and it will publish the 
# result of adding number+increment in a recursive way.
class VelToOdom():
    def __init__(self):
        """ Parameters
        """
        self.tf_prefix = rospy.get_param('tf_prefix', '')  # Reads the tf_prefix from the ROS namespace
        if self.tf_prefix is not '':
            self.tf_prefix = '/' + self.tf_prefix
        rospy.on_shutdown(self.cleanup)
        ###******* INIT PUBLISHERS *******###
        rospy.logdebug("Setting publishers...")
        self.pub_odom = rospy.Publisher('odom', Odometry, queue_size=10)
        ############################### SUBSCRIBERS #####################################
        rospy.Subscriber("cmd_vel", Twist, self.cmd_vel_cb)
        ############ CONSTANTS ################
        self.angular_vel = 0.0  #Angular vel about z in rad/s
        self.linear_vel = 1.0   #Linear vel in m/s
        self.positionx= 0.0     # The robot's estimated position in x
        self.positiony= 0.0     # The robot's estimated position in y
        self.orientationz= 0.0  # The robot's estimated orientation about z
        r = rospy.Rate(10)              #1Hz
        print "Node initialized 1hz"
        self.tf_broadcaster = tf.TransformBroadcaster()  # NOTE THIS: the listener should be declared in the class
        self.current_time=rospy.Time.now()
        odom_quat = Quaternion()
        odom_trans = TransformStamped()
        odom_msg_= Odometry()
        print "while"
        while not rospy.is_shutdown():
            print "time"
            self.prev_time=deepcopy(self.current_time)
            self.current_time=rospy.Time.now() #Get the current time to stamp it
            #Update the robot's pose
            delta_t=self.current_time.to_sec()-self.prev_time.to_sec()
            delta_theta=self.angular_vel*delta_t # d=v.t
            self.orientationz=self.orientationz+delta_theta
            #vx=v.cosQ  and vy=v.sinQ
            vx=self.linear_vel*np.cos(self.orientationz)
            vy=self.linear_vel*np.sin(self.orientationz)
            #d=v.t
            self.positionx=self.positionx+vx*delta_t
            self.positiony=self.positiony+vy*delta_t
            odom_quat=tf.transformations.quaternion_about_axis(self.orientationz,(0,0,1))
            
            # Create the odometry transformation
            parent_frame = self.tf_prefix + "/odom"
            child_frame = self.tf_prefix + "/base_link"
            translation=(self.positionx,self.positiony, 0.0)
            # send the transformation between odom and base_link
            try:
                self.tf_broadcaster.sendTransform(translation, odom_quat, self.current_time, child_frame, parent_frame )
            except:
                rospy.logerr("could not broadcast transformation")
            #Now send Odometry message and publish
            odom_msg_.pose.pose.position.x = self.positionx
            odom_msg_.pose.pose.position.y = self.positiony
            odom_msg_.pose.pose.position.z = 0.0
            odom_msg_.pose.pose.orientation = odom_quat
            odom_msg_.header.frame_id = self.tf_prefix + "/odom"
            odom_msg_.child_frame_id = self.tf_prefix + "/base_link"
            odom_msg_.header.stamp = self.current_time
            #The Odometry also has the velocities
            odom_msg_.twist.twist.linear.x =  self.linear_vel
            odom_msg_.twist.twist.linear.y =  0.0
            odom_msg_.twist.twist.angular.z = self.angular_vel
            self.pub_odom.publish(odom_msg_)
            
            r.sleep()

    def cmd_vel_cb(self, msg):
        ## This function receives a Twist and copies the linear and angular velocities
        self.linear_vel=msg.linear.x
        self.angular_vel=msg.angular.z
        


    def cleanup(self):
        #This function is called just before finishing the node
        # You can use it to clean things up before leaving
        # Example: stop the robot before finishing a node.	
        pass


############################### MAIN PROGRAM ####################################
if __name__ == "__main__":
    rospy.init_node("velocity2odom", anonymous=True)
    try:
	    VelToOdom()
    except:
        rospy.logfatal("velocity2odom died")