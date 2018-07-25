#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pyspin_wrapper.pyspin_library as wrapper

if __name__=="__main__":
	overhead_camera=wrapper.Pyspin_VideoCapture('overhead_camera',"18080264")
	overhead_camera.open_camera()
	overhead_camera.start_trigger_service()
