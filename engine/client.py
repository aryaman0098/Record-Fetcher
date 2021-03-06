import sys
from socket import *
from protocol import *

				
name=sys.argv[1]
lang=sys.argv[2]
email=sys.argv[3]
phone=sys.argv[4]
academic=sys.argv[5]
other=sys.argv[6]
auth=sys.argv[7]

d={'name':name,'lang':lang,'email':email,'phone':phone,'academic':academic,'other':other,'auth':auth}

for key in ['email','phone','academic','other']:
	if(d[key]=='0'):
		d.pop(key)

content={}
for i in d:
	if(i!='auth' and i!='lang'):
		content[i]=d[i]



serverName = '127.0.0.1'
serverPort = 12000

clientSocket = socket(AF_INET, SOCK_DGRAM)
request=Message(clientSocket,serverName,serverPort)
request.write_client(content,d['auth'],d['lang'])
request.read_client()
clientSocket.close()