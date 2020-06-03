SID1616658

This folder contains the source code the the Final Project module - MOD002691. 

Within door_graph_v2 folder you can find the optimised model which was converted using Intel OPENVINO toolkit:
 cameraServer.py - this is a python script for streaming the Pi camera to a local IP address on port 8080
 door_detector.py - this is an algorithm developed in python which utilises the optimised model to correctly predict detected doors, estimate the distance
 		    and provide haptic feedback as well as speech feedback to the user. 