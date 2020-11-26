import socket
import json
import pickle

host = socket.gethostname()
port = 12999

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect((host, port))


def json_decode(data):
    tiow = io.TextIOWrapper(io.BytesIO(data), encoding = "utf-8", newline="")
    obj = json.load(tiow)
    tiow.close()
    return obj


def retrieveData():
    while True:
        message = input("Enter the person whose number you want to find : ").lower()
        s.sendto(message.encode(), (host, port))
        if message == "Q" or message == "q":
            break
        data, addr = s.recvfrom(4096)
        msg = pickle.loads(data)
        if msg == None:
            print("An error again! Please try again")
        else:
            print(msg)

retrieveData()