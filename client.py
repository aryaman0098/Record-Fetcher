import socket
import json
import pickle
from protocol import * #Importing the protocol file

host = socket.gethostname()
port = 12999

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect((host, port))



def retrieveData():
    while True:
        Query = protocol() #Creating a object of type protocol
        Name = input("Enter the person whose number you want to find : ").lower() #Taking the user Entry corresponding to which he wants the data
        Query.fillHeaders(True, Name, "") #Filling the headers according to the input (Note -> True is for authentication, a feature that we will implement in fututre)
        s.sendto(pickle.dumps(Query), (host, port)) #Encoding and sending the query to the server
        if Query.query == "q": #For closing the connection
            s.close()
            break
        data, addr = s.recvfrom(4096) #Receiving the data from the server
        Msg = pickle.loads(data) #Decoding the data

        if Msg.response["Name"] == "No such name in directory!": #Checking if no name is present in the directory corresponding to the above given name
            print("Invalid name!")
        elif Msg.response["Name"] == "Error": #If data got lost while sending from client (Note -> this implementation is a bit faulty)
            print("Error occured! Retrying....")
            s.sendto(pickle.dumps(Query), (host, port)) #Resending the same query packet
        else:
            if Msg.header["responseLength"] == len(Msg.response): #Checking if the data received from server has o lost bits
                print(Msg.response)
            else: #If data has been lost, then resending the same query packet
                print("Error occured! Retrying....")
                s.sendto(pickle.dumps(Query), (host, port))
            
retrieveData()