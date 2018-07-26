

import pyspin_wrapper.pyspin_library as wrapper

import numpy as np
import cv2
import rospy
def image_save_and_load(image):
	image.Save("Testimage.jpg")
	loaded=cv2.imread("Testimage.jpg",1)
	return cv2.resize(loaded,(1920,1080))

if __name__== '__main__':
	camname="topcam"
	serialnum="18080264"
	print "hello"
	rospy.init_node('image_feature', anonymous=True)
	camera_obj=wrapper.Pyspin_VideoCapture(camname,serialnum,{})
	camera_obj.printall_camera_ids()
	
	

	camera_obj.open_camera()
	camera_obj.print_camera_values()
	

	#image_out=camera_obj.read_frame()
	
	camera_obj.publish_continuous()
	raw_input("press enter")
	#image_out=image_save_and_load(image_out)
	#cv2.imshow('image',image_out)
	#cv2.waitKey(0)
	#cv2.destroyAllWindows()
	
	camera_obj.release()
	
