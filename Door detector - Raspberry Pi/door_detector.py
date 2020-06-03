#Algorithm for running the object detector on the Pi - requires the NCS2
#USAGE: python3 door_detector.py 

running_on_rpi = False
import os

os_info = os.uname()
if os_info[4][:3] == 'arm':
    running_on_rpi = True

# import the necessary packages
from imutils.video import VideoStream
from imutils.video import FPS
from gpiozero import PWMOutputDevice
from gtts import gTTS
from tempfile import TemporaryFile

import argparse
import time
import cv2
import numpy as np
import socket

#function for making prediction using the NCS
def predict(frame, net):
    # Prepare input blob and perform an inference
    blob = cv2.dnn.blobFromImage(frame, size=(672, 384), ddepth=cv2.CV_8U)
    net.setInput(blob)
    out = net.forward()

    predictions = []

    # Draw detected doors on the frame
    for detection in out.reshape(-1, 7):
        conf = float(detection[2])
        xmin = int(detection[3] * frame.shape[1])
        ymin = int(detection[4] * frame.shape[0])
        xmax = int(detection[5] * frame.shape[1])
        ymax = int(detection[6] * frame.shape[0])

        if conf > args["confidence"]:
            pred_boxpts = ((xmin, ymin), (xmax, ymax))

            # create prediciton tuple and append the prediction to the
            # predictions list
            prediction = (conf, pred_boxpts)
            predictions.append(prediction)

    # return the list of predictions to the calling function
    return predictions

#function for calculating the distance
def distance_to_camera(knownWidth, focalLength, percivedWidth):
    #process and return distance from the door to the camera
    return(knownWidth * focalLength) / percivedWidth

#function for re-mapping the estimated distance to a value ranging between 0 - 1 for PWM
def calculate_vibration(distance):
    vibration = (((distance - 2) * -1) / (700 - 2)) + 1
    return vibration

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-c", "--confidence", default=.70,
                help="confidence threshold")
ap.add_argument("-d", "--display", type=int, default=0,
                help="switch to display image on screen")
ap.add_argument("-i", "--input", type=str,
                help="path to optional input video file")
args = vars(ap.parse_args())

# Load the model
net = cv2.dnn.readNet('door_graph_v2/frozen_inference_graph.xml', 'door_graph_v2/frozen_inference_graph.bin')

# Specify target device
net.setPreferableTarget(cv2.dnn.DNN_TARGET_MYRIAD)

#define vibration motors
motor_right = PWMOutputDevice(18)
motor_left = PWMOutputDevice(14)

#define socket address, port and connect
server_address = '127.0.0.1'
port = 54000

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((url, port))

#parameters for distance estimation 
knownWidth = 76
focalLength =  250

language = 'en'

# if a video path was not supplied, grab a reference to the webcam
if not args.get("input", False):
    print("[INFO] starting video stream...")
    
    #connect to local server for the video stream and capture the video
    cam = 'http://192.168.0.35:8080/stream.mjpg'
    vs = cv2.VideoCapture(cam)
    time.sleep(2.0)

# otherwise, grab a reference to the video file
else:
    print("[INFO] opening video file...")
    vs = cv2.VideoCapture(args["input"])

time.sleep(1)
fps = FPS().start()

# loop over frames from the video file stream
while True:
    try:
        # grab the frame from the threaded video stream
        # make a copy of the frame and resize it for display/video purposes
        ret, frame = vs.read()
        frame = frame[1] if args.get("input", False) else frame
        image_for_results = frame.copy()

        # use the NCS to acquire predictions
        predictions = predict(frame, net)

        # loop over our predictions
        for (i, pred) in enumerate(predictions):
            # extract prediction data for readability
            (pred_conf, pred_boxpts) = pred

            # filter out weak detections by ensuring the `confidence`
            # is greater than the minimum confidence
            if pred_conf > args["confidence"]:
                # print prediction to terminal
                print("[INFO] Prediction #{}: confidence={}, "
                      "boxpoints={}".format(i, pred_conf,
                                            pred_boxpts))

                # check if we should show the prediction data
                # on the frame
                if args["display"] > 0:
                    # build a label
                    label = "Door: {:.2f}%".format(pred_conf * 100)

                    # extract information from the prediction boxpoints
                    (ptA, ptB) = (pred_boxpts[0], pred_boxpts[1]) 
                    (startX, startY) = (ptA[0], ptA[1])
                    y = startY - 15 if startY - 15 > 15 else startY + 15

                    # display the rectangle and label text
                    cv2.rectangle(image_for_results, ptA, ptB,
                                  (255, 0, 0), 2)
                    cv2.putText(image_for_results, label, (startX, y),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
                    
                    #if door is detected, start sending packets to the server side
                    client_socket.send('detected'.encode())
                    
                    #calcualte pixel width and estimate distance
                    pixelWidth = ptB[0] - ptA[0]               
                    print('\n')
                    distance = distance_to_camera(knownWidth, focalLength, pixelWidth)
                    
                    #check if distance is smaller than 700 cm 
                    if distance < 700:
                        print('distance: ', round(distance,0), 'centimeters')
                        print('\n')
                        
                        vibration_left = calculate_vibration(distance)
                        vibration_right = calculate_vibration(distance)
                        
                        #for visualization only, print values on the terminal
                        print('Left vibration motor value: ', vibration_left)
                        print('Right vibration motor value: ', vibration_right)
                        print('\n')

                        #setup the text to speech message
                        voice_output = str(round(distance, 0)) + ' centimeters'

                        obj = gTTS(text = voice_output, lang = language, slow=False)    
                        f = TemporaryFile()

                        #play the message 
                        obj.write_to_fp(f)
                        os.system('mpg123 ' + f) 
                        
                        #or it can be saved to an mp3 file if the following lines are un commented
                        #file_distance = 'distance.mp3'
                        #obj.save(file_distance)
                        #os.system('mpg123 ' + file_distance) 

                    else:
                        print('Distacne cannot be calcualted')
                    try:
                        motor_left.value = vibration_left
                        motor_right.value = vibration_right

                    except:
                        pass
                                       
        # check if we should display the frame on the screen
        # with prediction data 
        if args["display"] > 0:
            # display the frame to the screen
            cv2.imshow("Output", frame)#image_for_result)
            key = cv2.waitKey(1) & 0xFF

            # if the `q` key was pressed, break from the loop
            if key == ord("q"):
                break

        # update the FPS counter
        fps.update()

    # if "ctrl+c" is pressed in the terminal, break from the loop
    except KeyboardInterrupt:
        break

    # if there's a problem reading a frame, break 
    except AttributeError:
        break

# stop the FPS counter timer
fps.stop()

# destroy all windows if we are displaying them
if args["display"] > 0:
    cv2.destroyAllWindows()

# if we are not using a video file, stop the camera video stream
if not args.get("input", False):
    vs.release()
    cv2.destroyAllWindows()
# otherwise, release the video file pointer
else:
    vs.release()

# display FPS information
print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
