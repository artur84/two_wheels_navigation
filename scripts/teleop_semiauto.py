#!/usr/bin/env python
import rospy
from geometry_msgs.msg import Twist
from std_msgs.msg import String
from copy import deepcopy
from visualization_msgs.msg._Marker import Marker
from visualization_msgs.msg._MarkerArray import MarkerArray
from nav2d_operator.msg import cmd
import tf
import sys, select, termios, tty

msg = """
Reading from the keyboard  and Publishing to Twist!
---------------------------
Moving around:
   u    i    o
   j    k    l
   m    ,    .

+/- : increase/decrease max speeds
space tab: change teleop mode
anything else : stop

CTRL-C to quit
"""
#(linear x, angular z, linear(cmd), Turn(cmd))
moveBindings = {
    'i':( 1,    0,   1,   0),
    'o':( 1,   -1,   1,   1),
    'l':( 0,   -1, 0.4,   1.5),
    '.':(-1,    1,  -1,  -1),
    ',':(-1,    0,  -1,   0),
    'm':(-1,    1,  -1,  -1),
    'j':( 0,    1, 0.4,  -1.5),
    'u':( 1,    1,   1,  -1),
    'k':( 0,    0,   0,   0),
       }

def getKey():
    tty.setraw(sys.stdin.fileno())
    select.select([sys.stdin], [], [], 0)
    key = sys.stdin.read(1)
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key

speed = 0.4 #[msec] linear speed multiplier
turn = 0.2 #[rad/sec] angular speed multiplier
turn_inc = 0.025 #increment for the angular vel when the +/- keys are pressed.
speed_inc = 0.05 #increment for the linear vel when the +/- keys are pressed.
mode = 0  #mode for the nav2D

def vels(speed, turn, mode):
    return "currently:\t speed: %s\t turn: %s\t mode: %s" % (speed, turn, mode)

if __name__ == "__main__":
    settings = termios.tcgetattr(sys.stdin)
    rospy.init_node('teleop_twist_keyboard')
    """ ROS Parameters
    """
    vel_pub = rospy.Publisher('key_vel', Twist, queue_size=10)
    nav2d_cmd_pub = rospy.Publisher('cmd', cmd, queue_size=10)

    x = 0
    th = 0
    status = 0
    try:
        print msg
        print vels(speed, turn, mode)
        key_vel = Twist()
        nav2d_cmd = cmd()
        while(1):
            key = getKey()
            if key in moveBindings.keys():
                x = moveBindings[key][0]
                th = moveBindings[key][1]
                key_vel.linear.x = x * speed; key_vel.linear.y = 0; key_vel.linear.z = 0
                key_vel.angular.x = 0; key_vel.angular.y = 0; key_vel.angular.z = th * turn
                vel_pub.publish(key_vel)
                #nav2d cmd velocity
                nav2d_cmd.Velocity=moveBindings[key][2]*speed
                nav2d_cmd.Turn = moveBindings[key][3]*turn
                nav2d_cmd.Mode = mode 
                nav2d_cmd_pub.publish(nav2d_cmd)

                print nav2d_cmd
                
            elif key == '+':
                speed = speed + speed_inc
                turn = turn + turn_inc

                print vels(speed, turn, mode)
                if (status == 14):
                    print msg
                status = (status + 1) % 15
                
                 
            elif key == '-':
                speed = speed + speed_inc
                turn = turn + turn_inc

                print vels(speed, turn, mode)
                if (status == 14):
                    print msg
                status = (status + 1) % 15
               

            elif key == ' ':
                if mode == 0:
                    mode=1
                else:
                    mode=0
                rospy.loginfo("mode: %d", mode)
                #nav2d cmd velocity
                nav2d_cmd.Velocity=moveBindings[key][2]*speed
                nav2d_cmd.Turn = moveBindings[key][3]*turn
                nav2d_cmd.Mode = mode 
                nav2d_cmd_pub.publish(nav2d_cmd)


            else:
                x = 0; th = 0
                dir_x = -1; dir_th = 0 #dir_x=-1 means this is not a valid key to give directions
                if (key == '\x03'):
                    break



    except:
        rospy.logerror("teleop_semiauto.py: exception")

    finally:
        key_vel = Twist()
       
        key_vel.linear.x = 0; key_vel.linear.y = 0; key_vel.linear.z = 0
        key_vel.angular.x = 0; key_vel.angular.y = 0; key_vel.angular.z = 0
        nav2d_cmd.Velocity=key_vel.linear.x; nav2d_cmd.Turn = key_vel.angular.z
        vel_pub.publish(key_vel)
        nav2d_cmd_pub.publish(nav2d_cmd)

        print key_vel
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
