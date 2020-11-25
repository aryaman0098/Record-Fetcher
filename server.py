import socket
from pymongo import MongoClient

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

createSocket()

while True:
    data, addr = s.recvfrom(4096)
    if data.decode() == "Q" or data.decode() == "q":
        s.close()
        break
    else:
        Name = str(data.decode())
        info = record.find_one({"Name" : Name})
        replyMsg = str(info["Number"])
        s.sendto(replyMsg.encode(), addr)
        