from socket import *
from protocol import *

serverName = gethostname()
serverPort = 12000
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))

print ('The server is ready to receive')
while True:
	request=protocol(serverSocket,serverName,serverPort)
	request.read_server()