from socket import *
from protocol import *



serverName='127.0.0.1'
serverPort = 12000
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))

while 1:
	request=Message(serverSocket,serverName,serverPort)
	request.read_server()

