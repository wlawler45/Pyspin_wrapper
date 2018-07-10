#!/usr/bin/env python
import PySpin
import numpy as np
import rospy
import time
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError


#create camera interface type and then append cameras using serial numbers from cameras

class Pyspin_VideoCapture:
	system = PySpin.System.GetInstance()
	
	cam_list = system.GetCameras()
	
	num_cameras = cam_list.GetSize()
	
	print num_cameras
	#designed to take camname, deviceserial number and dictionary of other camera parameters in as arguments and store them as attributes of the object
	def __init__(self,camname,deviceserial,params={}):
		self.bridge=CvBridge()
		self.image_pub=rospy.Publisher("/overhead_camera/Image",Image)
		self.camname=camname
		self.deviceserial=deviceserial
		#lets you assign the dictionary of camera params from the YAML file to this data structure
		self.params=params
		
		if Pyspin_VideoCapture.num_cameras == 0:

			# Clear camera list before releasing system
			Pyspin_VideoCapture.cam_list.Clear()

			# Release system
			Pyspin_VideoCapture.system.ReleaseInstance()
			raise Exception("No cameras connected")
        	#returns cam_list to allow use of cameras in API context
	def get_camera_list(self):
		return Pyspin_VideoCapture.cam_list
	
	#print deviceID and serial number of ALL connected cameras, not just the current object camera
	def printall_camera_ids(self):
		for i in range(Pyspin_VideoCapture.num_cameras):
			tempcam=Pyspin_VideoCapture.cam_list.GetByIndex(i)
			print "camera got"
			nodemap_tldevice = tempcam.GetTLDeviceNodeMap()
			device_id=""
			device_serial_number = ""
			node_device_id = PySpin.CStringPtr(nodemap_tldevice.GetNode("DeviceID"))
			if PySpin.IsAvailable(node_device_id) and PySpin.IsReadable(node_device_id):
				device_id = node_device_id.GetValue()
				print "Device ID retrieved as %s..." % device_id
			else:
				print "Device ID could not be retrieved"
			node_device_serial_number = PySpin.CStringPtr(nodemap_tldevice.GetNode("DeviceSerialNumber"))
			if PySpin.IsAvailable(node_device_serial_number) and PySpin.IsReadable(node_device_serial_number):
				device_serial_number = node_device_serial_number.GetValue()
				print "Device serial number retrieved as %s..." % device_serial_number
			else:
				print "Device serial number could not be retrieved"
			
	#print various camera parameters for specific camera, MUST BE CALLED AFTER OPEN CAM
	def print_camera_values(self):
		nodemap_tldevice = self.cam.GetTLDeviceNodeMap()
		node_device_information = PySpin.CCategoryPtr(nodemap_tldevice.GetNode("DeviceInformation"))
		if PySpin.IsAvailable(node_device_information) and PySpin.IsReadable(node_device_information):
			features = node_device_information.GetFeatures()
			for feature in features:
				node_feature = PySpin.CValuePtr(feature)
				print "%s: %s" % (node_feature.GetName(),
                                  node_feature.ToString() if PySpin.IsReadable(node_feature) else "Node not readable")

		else:
			print "Device control information not available."


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
			print "Unable to set acquisition mode to Single Frame (enum retrieval). Aborting..."
			return False

        # Retrieve entry node from enumeration node
		node_acquisition_mode_single = node_acquisition_mode.GetEntryByName("SingleFrame")
		if not PySpin.IsAvailable(node_acquisition_mode_single) or not PySpin.IsReadable(node_acquisition_mode_single):
			print "Unable to set acquisition mode to Single Frame (entry retrieval). Aborting..."
			return False

		# Retrieve integer value from entry node
		acquisition_mode_single = node_acquisition_mode_single.GetValue()

		# Set integer value from entry node as new value of enumeration node
		node_acquisition_mode.SetIntValue(acquisition_mode_single)
		self.cam.BeginAcquisition()
		image_result = self.cam.GetNextImage()
		image_converted = image_result.Convert(PySpinconversiontype, PySpincolorprocessing)
		image_result.Release()
		self.cam.EndAcquisition()
		return image_converted
		
	#designed to return a data stream or reference to data stream that can be used for videofeeds, try to use camera piping and specify lower resolution when using
	#def start_stream(self,device=0,pipe=0):

	def publish_image(self, PySpinconversiontype=PySpin.PixelFormat_Mono8,PySpincolorprocessing=PySpin.HQ_LINEAR):
		image=self.read_frame(PySpinconversiontype,Pyspincolorprocessing)
		
		frame = np.array(image.GetData(), dtype="uint8").reshape( (image.GetHeight(), image.GetWidth(),1))
		try:
	         self.image_pub.publish(self.bridge.cv2_to_imgmsg(cv_image, "mono8"))
		except CvBridgeError as e:
			print(e)
		
		
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


