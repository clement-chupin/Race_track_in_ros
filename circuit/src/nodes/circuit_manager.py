#!/usr/bin/env python3
from circuit.srv import StartRaceResponse,StartRace
import rospy 
import numpy as np
import rospy
from sensor_msgs.msg import Image
import cv2
from cv_bridge import CvBridge, CvBridgeError
import time
from PIL import Image as ImageConvert
import rospkg
import os


class Race_manager:
    def start_race(self,req):
        if rospy.get_time() - self.init_time > self.wait_before_race and not(self.finish):
            return StartRaceResponse(True)
        else:
            return StartRaceResponse(False)
               
    def get_image(self,time_left):
        photo_name = "lena"
        if self.finish:
            if self.blue_win:
                photo_name = "blue_win"
            else:
                photo_name = "red_win"
        else:
            
            if time_left < 9 and time_left > 8:
                photo_name = "9"
            if time_left < 8 and time_left > 7:
                photo_name = "8"
            if time_left < 7 and time_left > 6:
                photo_name = "7"
            if time_left < 6 and time_left > 5:
                photo_name = "6"
            if time_left < 5 and time_left > 4:
                photo_name = "5"
            if time_left < 4 and time_left > 3:
                photo_name = "4"
            if time_left < 3 and time_left > 2:
                photo_name = "3"
            if time_left < 2 and time_left > 1:
                photo_name = "2"
            if time_left < 1 and time_left > 0:
                photo_name = "1"
            if time_left < 0:
                photo_name = "go"
            else:
                print("time before start : ",time_left)

        rospack = rospkg.RosPack()
        circuit_path = rospack.get_path('circuit')
        self.image_name = cv2.imread(circuit_path+"/src/nodes/images/"+photo_name+".png")
        self.image_message = self.bridge.cv2_to_imgmsg(self.image_name, "bgr8")#passthrough
        return self.image_message

    def start_serv(self,):
        print("start server")

        self.init_time = rospy.get_time()
        s = rospy.Service('start_the_race', StartRace, self.start_race)

    def watch_finish(self,image_data):
        
        cv2_img = self.bridge.imgmsg_to_cv2(image_data, "bgr8")
        zone_x = 17
        zone_y = 19
        zone_x_size = 15
        zone_y_size = 2

        seuil = 2
        rouge_gagne = 0
        bleu_gagne = 0
        min_seuil = 80
        max_seuil = 150
        for i in range(zone_x_size):
            for j in range(zone_y_size):
                x = i + zone_x
                y = j + zone_y
                b = cv2_img[x][y][0]
                v = cv2_img[x][y][1]
                r = cv2_img[x][y][2]
                #print(r,v,b)
                if b > max_seuil and r < min_seuil and v < min_seuil:
                    bleu_gagne = bleu_gagne +1
                if r > max_seuil and b < min_seuil and v < min_seuil:
                    rouge_gagne = rouge_gagne +1
                cv2_img[x][y][0] = 0
                cv2_img[x][y][1] = 0
                cv2_img[x][y][2] = 255

        if bleu_gagne > seuil :
            self.finish = True
            self.blue_win = True
            print("les bleus gagnes")
        if rouge_gagne > seuil :
            self.finish = True
            self.red_win =True
            print("les rouges gagnes")
        # rospack = rospkg.RosPack()
        # filename = 'savedImage.png'
        # circuit_path = rospack.get_path('circuit')
        # cv2.imwrite(circuit_path+"/src/nodes/images/"+filename, cv2_img)
   
    def pub_image(self,):
        rate = rospy.Rate(2)
        self.image_pub = rospy.Publisher("/image_panel", Image, queue_size=1)
        while True:
            time_left = -((rospy.get_time() - self.init_time) - self.wait_before_race)
            
            self.image_pub.publish(self.get_image(time_left))
            rate.sleep()

    def __init__(self,):
        rospy.init_node("race_manager")
        self.bridge = CvBridge()
        self.wait_before_race = 35.0
        self.start_serv()
        self.finish = False
        self.blue_win = False
        self.red_win =False

        rospy.Subscriber('/race_track/finish_cam/image_raw', Image, self.watch_finish)
        
        self.pub_image()
        

        rospy.spin()

    
race = Race_manager()
