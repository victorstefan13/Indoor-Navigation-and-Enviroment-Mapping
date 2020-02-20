#ifndef SOCKET_H
#define SOCKET_H

int initSocket();

int fetchMsg(char buffer[4096], int clientSocket);

//void closeSess(int clientSocket);

#endif 
