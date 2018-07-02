import PySpin

#create camera interface type and then append cameras using serial numbers from cameras

class Pyspin_VideoCapture(object):
	system = PySpin.System.GetInstance()
	cam_list = system.GetCameras()
    num_cameras = cam_list.GetSize()
    #designed to take camname, deviceserial number and dictionary of other camera parameters in as arguments and store them as attributes of the object
	def __init__(self,camname,deviceserial,params={}):
		self.camname=camname
		self.deviceserial=deviceserial
		#lets you assign the dictionary of camera params from the YAML file to this data structure
		self.params=params
		
    	if num_cameras == 0:
			
        	# Clear camera list before releasing system
        	cam_list.Clear()

        	# Release system
        	system.ReleaseInstance()
        	raise Exception("No cameras connected")
        
	#returns cam_list to allow use of cameras in API context
	def get_camera_list(self):
		return cam_list
	
	#print deviceID and serial number of ALL connected cameras, not just the current object camera
	def printall_camera_ids(self):
		for i in range(num_cameras):
			tempcam=cam_list.GetByIndex(i)
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
			
	#print various camera parameters for specific camera
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
		cam=cam_list.GetBySerial(str(self.deviceserial))
		
		cam.Init()
		self.nodemap=cam.GetNodeMap()
		
		self.cam=cam
		
	#read_frame can be called with pyspin conversion and processing types defined in PySpin.py
	def read_frame(self,PySpinconversiontype=Pyspin.PixelFormat_Mono8,PySpincolorprocessing=PySpin.HQ_LINEAR):
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
		cam.EndAcquisition()
		return image_converted
		
	#designed to return a data stream or reference to data stream that can be used for videofeeds, try to use camera piping and specify lower resolution when using
	#def start_stream(self,device=0,pipe=0):
	
	#closes cameras correctly
	def release(self):
		for i in range(self.num_cameras):
			cam=self.cam_list.GetByIndex(i)
			cam.DeInit()
			del cam
		self.cam_list.Clear()
		self.system.ReleaseInstance()
		
	def __del__(self):
		self.release()
