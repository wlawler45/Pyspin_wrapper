from pyspin_library import Pyspin_VideoCapture
import numpy as np
import cv2

def image_save_and_load(image):
	image.Save("Testimage.jpg")
	return cv2.imread("Testimage.jpg",1)
	

if __name__== 'main':
	camname="topcam"
	serialnum="18080264"
	camera_obj=Pyspin_VideoCapture(camname,serialnum)
	camera_obj.printall_camera_ids()
	camera_obj.print_camera_values()
	camera_obj.open_camera()
	image_out=camera_obj.read_frame()
	
	#image_out=image_save_and_load(image_out)
	cv2.imshow('image',image_out)
	cv2.waitKey(0)
	cv2.destroyAllWindows()
	
	camera_obj.release()
	
