import socket
from pymongo import MongoClient
import json
import pickle
from protocol import *

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
        data, addr = s.recvfrom(4096)
        Query = pickle.loads(data)
        if Query.query == "q":
            s.close()
            break
        else:
            try:
                if Query.header["queryLength"] == len(Query.query):
                    info = record.find_one({"Name" : Query.query})
                    Response = protocol()
                    Response.fillHeaders(True, "", info)  
                    s.sendto(pickle.dumps(Response), addr)
                    print("Query completed!")
                else:
                    Response = protocol()
                    Response.fillHeaders(True, "", {"Message" : "Error"})  
                    s.sendto(pickle.dumps(Response), addr)
                    print("Query completed!")
            except:
                print("Query completed!")
                Response.fillHeaders(True, "", None)
                s.sendto(pickle.dumps(Response), addr)
                continue
        
createSocket()
addressQueries()