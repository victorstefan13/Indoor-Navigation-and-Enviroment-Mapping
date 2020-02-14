/*
This file was modified from mono_tum.cc within the ORB_SLAM2 github repository.
sdf */

//modified code for live detection

#include <iostream>
#include <algorithm> 
#include <fstream>
#include <chrono>
#include <opencv2/core/core.hpp>
#include <opencv2/opencv.hpp>
#include <System.h>

using namespace std;
int main(int argc, char **argv) 
{
   if(argc != 3) 
   {
     cerr << endl << "Usage: ./path_to_PF_ORB path_to_vocabulary path_to_settings path_to_dev_video" << endl;
     return 1;
   }
   cv::VideoCapture cap(1);
   if (!cap.isOpened())
   {
     cerr << endl  <<"Could not open camera feed."  << endl;
     return -1;
   }
   // Create SLAM system. It initializes all system threads and gets ready to process frames.
   ORB_SLAM2::System SLAM(argv[1],argv[2],ORB_SLAM2::System::MONOCULAR,true);

   cout << endl << "-------" << endl;
   cout << "Start processing sequence ..." << endl;

   // initialise TCP socket and set up buffer for message
   //int clientSock = SLAM.initSocket();
   char buf[4096];

   // Main loop
   int timeStamps=0;
   for(;;timeStamps++)
   {
     //Create a new Mat
     cv::Mat frame;

     //Send the captured frame to the new Mat
     cap>>frame;

     // Pass the image to the SLAM system
     SLAM.TrackMonocular(frame, timeStamps);

     //fetch the message from the python DL model
     //SLAM.fetchMsg(buf, clientSock);
    }

   // Stop all threads
   SLAM.Shutdown();

    // Save camera trajectory
    SLAM.SaveKeyFrameTrajectoryTUM("KeyFrameTrajectory.txt");
    return 0;
}
