#!/usr/bin/env python
# This file is a copy from the awesome work done by students of my Robotics Project Class of 2018.
# You can check the original file at the project_shark repository in github.
# This file publishes nav2d_operator messages to the /cmd topic when pressing a key.
import rospy
import math
from nav2d_operator.msg import cmd
import sys, select, termios, tty

global speed


def getKey():
   tty.setraw(sys.stdin.fileno())
   select.select([sys.stdin], [], [], 0)
   key = sys.stdin.read(1)
   termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
   return key

def go_forward(msg):
    msg.Velocity = speed
    msg.Turn = 0.0
    pub.publish(msg)

def go_backward(msg):
    msg.Velocity = -speed
    msg.Turn = 0.0
    pub.publish(msg)

def turn_right(msg):
    msg.Velocity = speed
    msg.Turn = 1.0
    pub.publish(msg)

def turn_left(msg):
    msg.Velocity = speed
    msg.Turn = -1.0
    pub.publish(msg)

def stop(msg):
    msg.Velocity = 0.0
    msg.Turn = 0.0
    pub.publish(msg)


def teleop():
    global pub
    global rate
    global speed

    speed = 0.4

    pub = rospy.Publisher('cmd', cmd, queue_size=10)

    rospy.init_node('teleop_nav2d', anonymous=True)

    msg = cmd()

    rate = rospy.Rate(100) # 10hz
    
    key = ""
    print("Use W,A,S,D and Space to move the robot")
    while not rospy.is_shutdown():
        key = "x"
        key = getKey()
        key = key.lower()
        if(key == 'w'):
            go_forward(msg)
        elif(key == 's'):
            go_backward(msg)
        elif(key == 'a'):
            turn_left(msg)
        elif(key == 'd'):
            turn_right(msg)
        elif(key == ' '):
            stop(msg)
        elif(key == '\x03'):
            break

        rate.sleep()

if __name__ == '__main__':
    try:
        settings = termios.tcgetattr(sys.stdin)
        teleop()
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    except rospy.ROSInterruptException:
        pass