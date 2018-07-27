#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pyspin_wrapper.pyspin_library as wrapper

if __name__=="__main__":
	overhead_camera=wrapper.Pyspin_VideoCapture('overhead_camera',"18080264")
	overhead_camera.open_camera()
	overhead_camera.start_trigger_service()
	'''gripper_cam_proximal=wrapper.Pyspin_VideoCapture('gripper_cam_proximal',"18285636")
	gripper_cam_proximal.open_camera()
	gripper_cam_proximal.start_trigger_service()
	gripper_cam_distal=wrapper.Pyspin_VideoCapture('gripper_cam_distal',"18285621")
	gripper_cam_distal.open_camera()
	gripper_cam_distal.start_trigger_service()'''
