#!/usr/bin/env python
# -*- coding: utf-8 -*-
import PySpin
import time

system = PySpin.System.GetInstance()
#rospy.init_node('image_feature', anonymous=True)
cam_list = system.GetCameras()

num_cameras = cam_list.GetSize()
PySpinconversiontype=PySpin.PixelFormat_Mono8
PySpincolorprocessing=PySpin.HQ_LINEAR
if num_cameras == 0:


    # Clear camera list before releasing system
    cam_list.Clear()

                # Release systerospy.Servicem
    system.ReleaseInstance()
    raise Exception("No cameras connected")
cam=cam_list.GetBySerial(str("18080264"))

cam.Init()
nodemap=cam.GetNodeMap()

node_acquisition_mode = PySpin.CEnumerationPtr(nodemap.GetNode("AcquisitionMode"))
if not PySpin.IsAvailable(node_acquisition_mode) or not PySpin.IsWritable(node_acquisition_mode):
    rospy.logerr("Unable to set acquisition mode to continuous (enum retrieval). Aborting...")
    

 # Retrieve entry node from enumeration node
node_acquisition_mode_continuous = node_acquisition_mode.GetEntryByName("Continuous")
if not PySpin.IsAvailable(node_acquisition_mode_continuous) or not PySpin.IsReadable(node_acquisition_mode_continuous):
    rospy.logerr("Unable to set acquisition mode to continuous (entry retrieval). Aborting...")
    
pixel_format= PySpin.CEnumerationPtr(nodemap.GetNode("PixelFormat"))
pixel_format_mode=pixel_format.GetEntryByName("Mono8")
pixel_format.SetIntValue(pixel_format_mode.GetValue())



node_binning_mode= PySpin.CEnumerationPtr(nodemap.GetNode("BinningSelector"))
if not PySpin.IsAvailable(node_binning_mode) or not PySpin.IsWritable(node_binning_mode):
    print "failed at first binning"
binning_mode=node_binning_mode.GetEntryByName("Sensor")
node_binning_mode.SetIntValue(binning_mode.GetValue())

vertical_binning_mode= PySpin.CIntegerPtr(nodemap.GetNode("BinningVertical"))
if not PySpin.IsAvailable(vertical_binning_mode) or not PySpin.IsWritable(vertical_binning_mode):
    print "failed at first vertical binning"
vertical_binning_mode.SetValue(2)
horizontal_binning_mode= PySpin.CIntegerPtr(nodemap.GetNode("BinningHorizontal"))
if not PySpin.IsAvailable(horizontal_binning_mode) or not PySpin.IsWritable(horizontal_binning_mode):
    print "failed at first horizontal binning"
horizontal_binning_mode.SetValue(2)

cam.BeginAcquisition()
image_result = cam.GetNextImage()



image_result.Save("binnedimage.jpg")
print image_result.GetHeight()
print image_result.GetWidth()
image_result.Release()
cam.EndAcquisition()

time.sleep(3)


vertical_binning_mode= PySpin.CIntegerPtr(nodemap.GetNode("BinningVertical"))
if not PySpin.IsAvailable(vertical_binning_mode) or not PySpin.IsWritable(vertical_binning_mode):
    print "failed at second vertical binning"
vertical_binning_mode.SetValue(1)
horizontal_binning_mode= PySpin.CIntegerPtr(nodemap.GetNode("BinningHorizontal"))
if not PySpin.IsAvailable(horizontal_binning_mode) or not PySpin.IsWritable(horizontal_binning_mode):
    print "failed at second horizontal binning"
horizontal_binning_mode.SetValue(1)
node_binning_mode= PySpin.CEnumerationPtr(nodemap.GetNode("BinningSelector"))
if not PySpin.IsAvailable(node_binning_mode) or not PySpin.IsWritable(node_binning_mode):
    print "failed at second binning"
binning_mode_all=node_binning_mode.GetEntryByName("Sensor")
node_binning_mode.SetIntValue(binning_mode_all.GetValue())

cam.BeginAcquisition()
image_result = cam.GetNextImage()



image_result.Save("fullimage.jpg")
print image_result.GetHeight()
print image_result.GetWidth()
image_result.Release()
cam.EndAcquisition()
cam.DeInit()
del cam
cam_list.Clear()
system.ReleaseInstance()
