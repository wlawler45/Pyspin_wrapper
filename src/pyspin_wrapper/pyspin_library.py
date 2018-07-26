#!/usr/bin/env python
import PySpin
import numpy as np
import rospy
import time
from sensor_msgs.msg import Image, CompressedImage
from cv_bridge import CvBridge, CvBridgeError
import cv2
#from std_srvs.srv import Trigger
from pyspin_wrapper.srv import CameraTrigger
from PIL import Image as pic
#from actionlib import SimpleActionServer
#from multiprocessing import Process
    
#create camera interface type and then append cameras using serial numbers from cameras

class Pyspin_VideoCapture:
	system = PySpin.System.GetInstance()
	#rospy.init_node('image_feature', anonymous=True)
	cam_list = system.GetCameras()
	
	num_cameras = cam_list.GetSize()
	
	#print num_cameras
	#designed to take camname, deviceserial number and dictionary of other camera parameters in as arguments and store them as attributes of the object
	def __init__(self,camname,deviceserial,params={}):
		self.bridge=CvBridge()
		topicname="/"+camname+"/image"
		self.image_pub=rospy.Publisher(topicname,Image)
		self.compressed_image_pub=rospy.Publisher(topicname+'_compressed', CompressedImage)
		#self.tag_pose_pub=rospy.Publisher("ar_tag_pose",PoseStamped
		self.camname=camname
		self.deviceserial=deviceserial
		#lets you assign the dictionary of camera params from the YAML file to this data structure
		self.params=params
		
		if Pyspin_VideoCapture.num_cameras == 0:

			# Clear camera list before releasing system
			Pyspin_VideoCapture.cam_list.Clear()

                        # Release systerospy.Servicem
			Pyspin_VideoCapture.system.ReleaseInstance()
			raise Exception("No cameras connected")
        	#returns cam_list to allow use of cameras in API context

	def CameraParams(self, M00,M02,M11,M12,M22,C00,C01,C02,C03,C04):
		camMatrix = np.zeros((3, 3),dtype=np.float64)
		camMatrix[0][0] = M00
		camMatrix[0][2] = M02
		camMatrix[1][1] = M11
		camMatrix[1][2] = M12
		camMatrix[2][2] = M22

		distCoeff = np.zeros((1, 5), dtype=np.float64)
		distCoeff[0][0] = C00
		distCoeff[0][1] = C01
		distCoeff[0][2] = C02
		distCoeff[0][3] = C03
		distCoeff[0][4] = C04
            
		#        params = {'camMatrix': camMatrix, 'distCoeff': distCoeff}
		return camMatrix,distCoeff

	def get_camera_list(self):
		return Pyspin_VideoCapture.cam_list
	
	#print deviceID and serial number of ALL connected cameras, not just the current object camera
	def printall_camera_ids(self):
		for i in range(Pyspin_VideoCapture.num_cameras):
			tempcam=Pyspin_VideoCapture.cam_list.GetByIndex(i)
			#print "camera got"
			nodemap_tldevice = tempcam.GetTLDeviceNodeMap()
			device_id=""
			device_serial_number = ""
			node_device_id = PySpin.CStringPtr(nodemap_tldevice.GetNode("DeviceID"))
			if PySpin.IsAvailable(node_device_id) and PySpin.IsReadable(node_device_id):
				device_id = node_device_id.GetValue()
				rospy.loginfo("Device ID retrieved as %s...",  device_id)
			else:
				rospy.logerr("Device ID could not be retrieved")
			node_device_serial_number = PySpin.CStringPtr(nodemap_tldevice.GetNode("DeviceSerialNumber"))
			if PySpin.IsAvailable(node_device_serial_number) and PySpin.IsReadable(node_device_serial_number):
				device_serial_number = node_device_serial_number.GetValue()
				rospy.loginfo("Device serial number retrieved as %s...", device_serial_number)
			else:
				rospy.logerr( "Device serial number could not be retrieved")
			
	#print various camera parameters for specific camera, MUST BE CALLED AFTER OPEN CAM
	def print_camera_values(self):
		nodemap_tldevice = self.cam.GetTLDeviceNodeMap()
		node_device_information = PySpin.CCategoryPtr(nodemap_tldevice.GetNode("DeviceInformation"))
		if PySpin.IsAvailable(node_device_information) and PySpin.IsReadable(node_device_information):
			features = node_device_information.GetFeatures()
			for feature in features:
				node_feature = PySpin.CValuePtr(feature)
				rospy.loginfo( "%s: %s" ,(node_feature.GetName(),
                                  node_feature.ToString() if PySpin.IsReadable(node_feature) else "Node not readable")

		else:
			rospy.logerr( "Device control information not available.")


	#initializes camera, proper order is to instantialize object for each camera, call open_camera for every camera
	def open_camera(self):
		cam=Pyspin_VideoCapture.cam_list.GetBySerial(str(self.deviceserial))
		
		cam.Init()
		self.nodemap=cam.GetNodeMap()
		
		self.cam=cam
		
	#read_frame can be called with pyspin conversion and processing types defined in PySpin.py
	def read_frame(self,PySpinconversiontype=PySpin.PixelFormat_Mono8,PySpincolorprocessing=PySpin.HQ_LINEAR):
		node_acquisition_mode = PySpin.CEnumerationPtr(self.nodemap.GetNode("AcquisitionMode"))
		if not PySpin.IsAvailable(node_acquisition_mode) or not PySpin.IsWritable(node_acquisition_mode):
			rospy.logerr("Unable to set acquisition mode to continuous (enum retrieval). Aborting...")
			return False

        # Retrieve entry node from enumeration node
		node_acquisition_mode_continuous = node_acquisition_mode.GetEntryByName("Continuous")
		if not PySpin.IsAvailable(node_acquisition_mode_continuous) or not PySpin.IsReadable(node_acquisition_mode_continuous):
			rospy.logerr("Unable to set acquisition mode to continuous (entry retrieval). Aborting...")
			return False

		# Retrieve integer value from entry node
		acquisition_mode_continuous = node_acquisition_mode_continuous.GetValue()

		# Set integer value from entry node as new value of enumeration node
		node_acquisition_mode.SetIntValue(acquisition_mode_continuous)
		self.cam.BeginAcquisition()
		image_result = self.cam.GetNextImage()
		image_converted = image_result.Convert(PySpinconversiontype, PySpincolorprocessing)
		image_result.Release()
		self.cam.EndAcquisition()
		return image_converted
		
	#designed to return a data stream or reference to data stream that can be used for videofeeds, try to use camera piping and specify lower resolution when using
	#def start_stream(self,device=0,pipe=0):
	def continuous_capture(self):
		node_acquisition_mode = PySpin.CEnumerationPtr(self.nodemap.GetNode("AcquisitionMode"))
		if not PySpin.IsAvailable(node_acquisition_mode) or not PySpin.IsWritable(node_acquisition_mode):
			rospy.logerr("Unable to set acquisition mode to continuous (enum retrieval). Aborting...")
			return False

		# Retrieve entry node from enumeration node
		node_acquisition_mode_continuous = node_acquisition_mode.GetEntryByName("Continuous")
		if not PySpin.IsAvailable(node_acquisition_mode_continuous) or not PySpin.IsReadable(node_acquisition_mode_continuous):
			rospy.logerr("Unable to set acquisition mode to continuous (entry retrieval). Aborting...")
			return False

		# Retrieve integer value from entry node
		acquisition_mode_continuous = node_acquisition_mode_continuous.GetValue()

		# Set integer value from entry node as new value of enumeration node
		node_acquisition_mode.SetIntValue(acquisition_mode_continuous)
		self.cam.BeginAcquisition()
		while not rospy.is_shutdown():
			image=self.read_frame()
			image_result = self.cam.GetNextImage()
			image_converted = image_result.Convert(PySpinconversiontype, PySpincolorprocessing)
			frame = np.array(image_converted.GetData(), dtype="uint8").reshape( (image_converted.GetHeight(), image_converted.GetWidth(),1))
			try:
				self.image_pub.publish(self.bridge.cv2_to_imgmsg(frame, "mono8"))
			except CvBridgeError as e:
				return False, "Image Pub failed"
			image_result.Release()
		self.cam.EndAcquisition()



	def publish_image(self, req, trigger):
		if(trigger):
			if(req.continuous):
				self.continuous_capture()

			else:
				image=self.read_frame()
				frame = np.array(image.GetData(), dtype="uint8").reshape( (image.GetHeight(), image.GetWidth(),1))
				im=pic.fromarray(frame)
				compressed_msg=CompressedImage()
				compressed_msg.header.stamp = rospy.Time.now()
				compressed_msg.format='jpeg'
				compressed_msg.data=im
				try:
					self.image_pub.publish(self.bridge.cv2_to_imgmsg(frame, "mono8"))
					self.compressed_image_pub.publish(compressed_msg)
				except CvBridgeError as e:
					return False, "Image Pub failed"
				return True, "Trigger Received"
		else:
			image=self.read_frame()
			frame = np.array(image.GetData(), dtype="uint8").reshape( (image.GetHeight(), image.GetWidth(),1))
			im=pic.fromarray(frame)
			compressed_msg=CompressedImage()
			compressed_msg.header.stamp = rospy.Time.now()
			compressed_msg.format='jpeg'
			compressed_msg.data=im
			try:
				self.image_pub.publish(self.bridge.cv2_to_imgmsg(frame, "mono8"))
				self.compressed_image_pub.publish(compressed_msg)
			except CvBridgeError as e:
				return False, "Image Pub failed"
			return True, "Trigger Received"



	def start_trigger_service(self):
		rospy.init_node(self.camname+'/camera_trigger')
		s=rospy.Service(self.camname+'/camera_trigger', Trigger, self.publish_image(False))
		rospy.init_node(self.camname+'/continuous_trigger')
		s=rospy.Service(self.camname+'/continuous_trigger', CameraTrigger, self.publish_image(True))
		rospy.loginfo(self.camname+' Trigger service ready')
		rospy.spin()
		
	#closes cameras correctly
	def release(self):
		for i in range(Pyspin_VideoCapture.num_cameras):
			cam=Pyspin_VideoCapture.cam_list.GetByIndex(i)
			cam.DeInit()
			del cam
		Pyspin_VideoCapture.cam_list.Clear()
		Pyspin_VideoCapture.system.ReleaseInstance()
		
	#def __del__(self):
	#	self.release()

def print_triggered(hello):
	print "trigger received"
	return True, "Trigger received"

def start_service():
        rospy.init_node('camera_trigger')
	s=rospy.Service('camera_trigger', Trigger, print_triggered)
	print "Ready to trigger camera"
	rospy.spin()

'''if __name__=="__main__":
	overhead_camera=Pyspin_VideoCapture('overhead_camera',"18080264")
	overhead_camera.open_camera()
	overhead_camera.start_trigger_service()

	gripper_camera1=Pyspin_VideoCapture('gripper_camera1',"18285636")
	gripper_camera1.open_camera()
	gripper_camera1.start_trigger_service()
	gripper_camera2=Pyspin_VideoCapture('gripper_camera2',"18285621")
	gripper_camera2.open_camera()
	gripper_camera2.start_trigger_service()

#	start_service()
'''
