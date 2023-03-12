#!/usr/bin/env python3
from sensor_msgs.msg import Joy
import rospy
from std_msgs.msg import String
from sensor_msgs.msg import LaserScan,Range
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Image
from circuit.srv import StartRaceResponse,StartRace
import numpy as np

class Controlleur:
    def call_service(self,):
        savoir_si_la_course_commence = rospy.ServiceProxy("/circuit/start_the_race",StartRace)
        resp = savoir_si_la_course_commence()
        self.start = resp.result

    def joy_control(self,msg):
        # Create a publisher which can "talk" to Turtlesim and tell it to move
        move_cmd = Twist()
        move_cmd.linear.x = 0
        move_cmd.angular.z = 0
        if self.start:
            move_cmd.linear.x = msg.axes[2]
            move_cmd.angular.z = msg.axes[0]
            self.mvt.publish(move_cmd)
        self.call_service()

    def __init__(self):
        self.range_front =0
        self.range_right =0
        self.range_left =0
        self.start = False

        rospy.init_node("control_by_joy", anonymous=True)
        self.node_name = rospy.get_name()
        self.robot_index = rospy.get_param(self.node_name+"/robot_index")
        self.mvt = rospy.Publisher(str('/robot_'+str(self.robot_index)+'/cmd_vel'), Twist, queue_size=1)
        rospy.Subscriber("joy",Joy,self.joy_control,queue_size =10)
            
        rospy.spin()

contro = Controlleur()

