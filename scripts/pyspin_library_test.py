

import pyspin_wrapper.pyspin_library as wrapper

import numpy as np
import cv2
import rospy
def image_save_and_load(image):
	image.Save("Testimage.jpg")
	loaded=cv2.imread("Testimage.jpg",1)
	return cv2.resize(loaded,(1920,1080))

if __name__== '__main__':
	overhead_camera=wrapper.Pyspin_VideoCapture('overhead_camera',"18080264")
	overhead_camera.open_camera()
	

	#image_out=camera_obj.read_frame()
	
	camera_obj.publish_continuous()
	raw_input("press enter")
	#image_out=image_save_and_load(image_out)
	#cv2.imshow('image',image_out)
	#cv2.waitKey(0)
	#cv2.destroyAllWindows()
	
	camera_obj.release()
	
