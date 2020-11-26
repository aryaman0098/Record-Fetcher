import socket
from pymongo import MongoClient
import json
import pickle
from protocol import * #Importing the protocol file

mdbClient = MongoClient("mongodb+srv://Test:Test@cluster0.v7zkv.mongodb.net/<dbname>?retryWrites=true&w=majority")
db = mdbClient.get_database("Office_Bearer_Info")
record = db.Employee_Records


def createSocket():
    try:
        global host
        global port
        global s
        host = socket.gethostname()
        port = 12999
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind((host, port))
    
    except socket.error() as msg:
        print("Error occurred during creation of socket : " + str(msg))



def addressQueries():
    while True: 
        data, addr = s.recvfrom(4096) #Receiving data from client
        Query = pickle.loads(data) #Decoding the data
        if Query.query == "q": #For terminating the connection
            s.close()
            break
        else:
            try:
                if Query.header["queryLength"] == len(Query.query): #If data is intact (Note -> Implementation is faulty)
                    info = record.find_one({"Name" : Query.query}) #Fetching the data entry corresponding to the query name
                    Response = protocol() #Creating a response object of type protocol
                    Response.fillHeaders(True, "", info) #Filling the required headers (Note -> True is only for authentication)
                    s.sendto(pickle.dumps(Response), addr) #Sending the response data to the client
                    print("Query completed!")
                else:  #If data has been lost from client side(Note -> Implementation is faulty)
                    Response = protocol() 
                    Response.fillHeaders(True, "", {"Name" : "Error"})  
                    s.sendto(pickle.dumps(Response), addr)
                    print("Query completed!")
            except:  #If the requested name is not present in the databse
                print("Query completed!")
                Response.fillHeaders(True, "", {"Name" : "No such name in directory!"})
                s.sendto(pickle.dumps(Response), addr)
                continue
        
createSocket()
addressQueries()