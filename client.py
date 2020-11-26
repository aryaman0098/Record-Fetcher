import socket
import json
import pickle
from protocol import *

host = socket.gethostname()
port = 12999

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect((host, port))



def retrieveData():
    while True:
        Query = protocol()
        Name = input("Enter the person whose number you want to find : ").lower()
        Query.fillHeaders(True, Name, "")
        s.sendto(pickle.dumps(Query), (host, port))
        if Query.query == "q":
            s.close()
            break
        data, addr = s.recvfrom(4096)
        Msg = pickle.loads(data)
        if Msg.response == None:
            print("Invalid name!")
        elif Msg.response["Message"] == "Error":
            print("Error occured!")
        else:
            if Msg.header["responseLength"] == len(Msg.response):
                print(Msg.response)
            else:
                print("Sorry an error occurred! Please try again")
            
retrieveData()