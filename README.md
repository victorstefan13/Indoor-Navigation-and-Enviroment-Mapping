# Indoor-Navigation-and-Enviroment-Mapping using SLAM and Deep Learning

This project develops a software implementation using modern Computer Vision and Robotic Vision techniques to help guide the visually
impaired through internal unknown environments. The system features a Raspberry Pi for capturing the environment data through a monocular
camera, DNN (Deep Neural Networks) for object detection and SLAM (Simultaneous Localisation and Mapping) for environment mapping and
localisation. The system is used through internal environments and correctly detect doors within such environments, acknowledging the#
doors and pinpointing them on the map produced by the SLAM algorithm. Network programming is used to bind the DNN and SLAM algorithm
together and the distance from the user to the detected door is estimated using the information collected though the object detector.
