#!/usr/bin/env python
import PySpin
import numpy as np
import rospy
import time
import threading
from sensor_msgs.msg import Image, CompressedImage
from cv_bridge import CvBridge, CvBridgeError
import cv2
from std_srvs.srv import SetBool,Trigger
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
        imagestream="/"+camname+"/image_stream"
        self.image_pub=rospy.Publisher(topicname,Image,queue_size=100)
        self.stream_pub=rospy.Publisher(imagestream,Image,queue_size=100)
        self.compressed_image_pub=rospy.Publisher(topicname+'_compressed', CompressedImage,queue_size=100)
        self.compressed_image_stream=rospy.Publisher(imagestream+'_compressed',CompressedImage,queue_size=100)
        #self.tag_pose_pub=rospy.Publisher("ar_tag_pose",PoseStamped
        self.camname=camname
        self.deviceserial=deviceserial
        #lets you assign the dictionary of camera params from the YAML file to this data structure
        self.params=params
        self.PySpinconversiontype=PySpin.PixelFormat_Mono8
        self.PySpincolorprocessing=PySpin.HQ_LINEAR
        self.first_capture=True
        self.midstream_trigger=False
        self.continuous_capturing=False
        self.continuous_capture_lock=threading.Lock()
        self.continuous_capture_start=threading.Event()
        


        if Pyspin_VideoCapture.num_cameras == 0:


            # Clear camera list before releasing system
            Pyspin_VideoCapture.cam_list.Clear()

                        # Release systerospy.Servicem
            Pyspin_VideoCapture.system.ReleaseInstance()
            raise Exception("No cameras connected")
            #returns cam_list to allow use of cameras in API context

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
                                  node_feature.ToString() if PySpin.IsReadable(node_feature) else "Node not readable"))

        else:
            rospy.logerr( "Device control information not available.")


	#initializes camera, proper order is to instantialize object for each camera, call open_camera for every camera
    def open_camera(self):
        cam=Pyspin_VideoCapture.cam_list.GetBySerial(str(self.deviceserial))

        cam.Init()
        self.nodemap=cam.GetNodeMap()
        self.cam=cam

        node_acquisition_mode = PySpin.CEnumerationPtr(self.nodemap.GetNode("AcquisitionMode"))
        if not PySpin.IsAvailable(node_acquisition_mode) or not PySpin.IsWritable(node_acquisition_mode):
            rospy.logerr("Unable to set acquisition mode to continuous (enum retrieval). Aborting...")
            return False

         # Retrieve entry node from enumeration node
        node_acquisition_mode_continuous = node_acquisition_mode.GetEntryByName("Continuous")
        if not PySpin.IsAvailable(node_acquisition_mode_continuous) or not PySpin.IsReadable(node_acquisition_mode_continuous):
            rospy.logerr("Unable to set acquisition mode to continuous (entry retrieval). Aborting...")
            return False
        
        #node_binning_mode= PySpin.CEnumerationPtr(self.nodemap.GetNode("BinningSelector"))
        #binning_mode=node_binning_mode.GetEntryByName("Sensor")
        #node_binning_mode.SetIntValue(binning_mode.GetValue())
        #vertical_binning_mode= PySpin.CIntegerPtr(self.nodemap.GetNode("BinningHorizontal"))
        
        #vertical_binning_mode.SetValue(2)
        
        

        # Retrieve integer value from entry node
        acquisition_mode_continuous = node_acquisition_mode_continuous.GetValue()

        # Set integer value from entry node as new value of enumeration node
        node_acquisition_mode.SetIntValue(acquisition_mode_continuous)
		
	#read_frame can be called with pyspin conversion and processing types defined in PySpin.py
    def read_frame(self):
        if not self.midstream_trigger:

            self.cam.BeginAcquisition()
       
        if(self.first_capture):
            for i in range(3):
                throwaway_frame=self.cam.GetNextImage()
                time.sleep(1)
            self.first_capture=False
        image_result = self.cam.GetNextImage()
        
        image_converted = image_result.Convert(self.PySpinconversiontype, self.PySpincolorprocessing)
        image_converted.Save("testimage.jpg")
        image_result.Release()
        
        if not self.midstream_trigger:
            self.cam.EndAcquisition()
        return image_converted
		
    #designed to return a data stream or reference to data stream that can be used for videofeeds, try to use camera piping and specify lower resolution when using
    #def start_stream(self,device=0,pipe=0):
    def continuous_capture(self):
        

            
        self.first_capture=False

        self.cam.BeginAcquisition()
        rospy.loginfo("Beginning Acquisition")

        while self.continuous_capturing:


            self.continuous_capture_start.wait()
                #condition.wait()
            #while self.continuous_capturing:
            
            image_result = self.cam.GetNextImage()
            image_converted = image_result.Convert(self.PySpinconversiontype, self.PySpincolorprocessing)
            frame = np.array(image_converted.GetData(), dtype="uint8").reshape( (image_converted.GetHeight(), image_converted.GetWidth(),1))
            resized=cv2.resize(frame,(image_converted.GetWidth()/16,image_converted.GetHeight()/16))
            
            try:
                self.stream_pub.publish(self.bridge.cv2_to_imgmsg(resized, "mono8"))
            except CvBridgeError as e:
                return False, "Image Pub failed"

            image_result.Release()


        self.cam.EndAcquisition()



    def publish_image(self, req):
        #self.continuous_capture()
        #bool hello
        #hello=req.continuous
        rospy.loginfo("image service call received, taking pictures")
        

        if(req.continuous):
            self.continuous_capturing= not self.continuous_capturing

            if self.continuous_capturing:
                self.continuous_capture_thread=threading.Thread(target=self.continuous_capture)
                self.continuous_capture_thread.daemon=True
                self.continuous_capture_thread.start()
                self.continuous_capture_start.set()
            else:
                self.continuous_capture_start.clear()
            return True, "Trigger Received"

            #else:
             #   with self.continuous_capture_condition:
              #      self.continuous_capture_condition.wait()



			
        else:
            rospy.loginfo("Taking one picture")
            if self.continuous_capturing:
                self.continuous_capture_start.clear()
                rospy.loginfo("stopping midstream")
                self.midstream_trigger=True
                
            image=self.read_frame()
            frame = np.array(image.GetData(), dtype="uint8").reshape( (image.GetHeight(), image.GetWidth()))
            print image.GetHeight()
            print image.GetWidth()
            im=pic.fromarray(frame.astype(np.uint8))
            compressed_msg=CompressedImage()
            compressed_msg.header.stamp = rospy.Time.now()
            compressed_msg.format='jpeg'
            compressed_msg.data=im.tobytes()
            image_msg=Image()

            image_msg=self.bridge.cv2_to_imgmsg(frame,"mono8")
            image_msg.header.stamp=rospy.Time.now()

            try:
                self.image_pub.publish(image_msg)
                self.compressed_image_pub.publish(compressed_msg)
            except CvBridgeError as e:
                return False, "Image Pub failed"
            

            if self.midstream_trigger:
                self.continuous_capture_start.set()
                rospy.loginfo("resuming stream")
                self.midstream_trigger=False

            return True, "Trigger Received"

    def start_trigger_service(self):
        #rospy.init_node('camera_trigger')
        #s=rospy.Service(self.camname+'/camera_trigger', Trigger, self.publish_image())
        rospy.init_node('continuous_trigger')
        s=rospy.Service(self.camname+'/continuous_trigger', CameraTrigger, self.publish_image)
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
