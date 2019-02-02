from cscore import CameraServer

import cv2
import numpy as np

def main():
	resW = 544
	resH = 306
	fps = 30
	cs = CameraServer.getInstance()
	cs.enableLogging()
	
	camera = cs.startAutomaticCapture()
	camera.setResolution(resW, resH)
	camera.setFPS(fps)
	
	cvSink = cs.getVideo()
	
	outputStream = cs.putVideo("Name", resW, resH)
	
	img = np.zeros(shape=(resH, resW, 3), dtype=np.uint8)
	
	while(True):
		time, img = cvSink.grabFrame(img)
		if time == 0:
			outputStream.notifyError(cvSink.getError());
			continue
			
			#if we ever need to vision processing code, put it here.
			
			
			
			outputStream.putFrame(img)

