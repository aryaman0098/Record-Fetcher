import socket
from pymongo import MongoClient
import json
import pickle

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
        Name = data.decode()
        if Name == "Q" or Name == "q":
            s.close()
            break
        else:
            try:
                info = record.find_one({"Name" : Name})
                s.sendto(pickle.dumps(info), addr)
                print("Query completed!")
            except:
                print("Query completed!")
                replyMsg = None
                s.sendto(pickle.dumps(replyMsg), addr)
                continue
        
createSocket()
addressQueries()