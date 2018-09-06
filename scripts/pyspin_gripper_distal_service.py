#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pyspin_wrapper.pyspin_library as wrapper

if __name__=="__main__":
	gripper_cam_distal=wrapper.Pyspin_VideoCapture('gripper_camera_1',"18285621")
	gripper_cam_distal.open_camera()
	gripper_cam_distal.start_trigger_service()
