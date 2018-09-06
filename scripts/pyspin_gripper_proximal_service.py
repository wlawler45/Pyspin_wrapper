#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pyspin_wrapper.pyspin_library as wrapper

if __name__=="__main__":
	gripper_cam_proximal=wrapper.Pyspin_VideoCapture('gripper_camera_2',"18285636")
	gripper_cam_proximal.open_camera()
	gripper_cam_proximal.start_trigger_service()

