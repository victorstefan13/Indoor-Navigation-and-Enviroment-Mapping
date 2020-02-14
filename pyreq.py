import socket

url = '127.0.0.1'
port = 54000

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((url, port))
data = ''

while True:
    s.send('Hello World! This is a test!'.encode()) 
    data = s.recv(1024).decode()
    print (data)

s.close()