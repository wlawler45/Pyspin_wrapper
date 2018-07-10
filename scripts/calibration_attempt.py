import pyspin_wrapper.pyspin_library as wrapper
import arm_composites_manufacturing_controller_commander as controller_commander_pkg
import os
import errno
import rospy
import cv2.aruco as aruco
import cv2
import numpy as np
if __name__== '__main__':
	rospy.init_node('calibration_attempt.py', anonymous=True)
	camname="topcam"
	serialnum="18080264"
	camera_obj=wrapper.Pyspin_VideoCapture(camname,serialnum,{})
	camera_obj.open_camera()
	robot_poses=[]
	controller_commander=controller_commander_pkg.arm_composites_manufacturing_controller_commander()
	foldername='calibration_data'
	filename="robot_poses"
	

	for i in range(20):
		exitnow=raw_input("Move robot t
o position and press enter to continue or type exit to quit")
		if exitnow.lower()=="exit":
			break
		
		image_out=camera_obj.read_frame()
		frame = np.array(image_out.GetData(), dtype="uint8").reshape( (image_out.GetHeight(), image_out.GetWidth(),1))

		aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)
		parameters =  aruco.DetectorParameters_create()
		corners, ids, rejectedImgPoints = aruco.detectMarkers(frame, aruco_dict, parameters=parameters)
		
		if ids is None:
			ids=[]
		if len(ids)!=4:
			print str(len(ids))+ " tags seen, try again"
			continue
		print ids
		savename="Calibration_photo-"+str(i)+".jpg"
		image_out.Save(savename)
		posedata=controller_commander.get_current_pose_msg() 
		print posedata
		print "Image number:" +str(i)+" captured"
		robot_poses.append(posedata)
	with open(filename, "w") as f:
		for x in range(len(robot_poses)):
			f.write("Calibration Pose: "+str(x)+"\n")
			f.write(str(robot_poses[x]))
	camera_obj.release()
	
