#!/usr/bin/env python
import pyspin_wrapper.pyspin_library as wrapper
from std_srvs.srv import Trigger
import numpy as np
import cv2
import rospy
def image_save_and_load(image):
	image.Save("Testimage.jpg")
	loaded=cv2.imread("Testimage.jpg",1)
	return cv2.resize(loaded,(1920,1080))

def camera_trigger_client():
	rospy.wait_for_service('camera_trigger')
	camera_trigger=rospy.ServiceProxy('camera_trigger', Trigger)
	s=camera_trigger()
	#print camera_trigger.success
	#print camera_trigger.message
		

if __name__== '__main__':
	while(True):

		camera_trigger_client()
	
	#image_out=image_save_and_load(image_out)
	#cv2.imshow('image',image_out)
	#cv2.waitKey(0)
	#cv2.destroyAllWindows()
	
	
