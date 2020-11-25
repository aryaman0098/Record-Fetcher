import socket

host = socket.gethostname()
port = 12999

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect((host, port))
while True:
    message = input("Enter the person whose number you want to find : ")
    s.sendto(message.encode(), (host, port))
    if message == "Q" or message == "q":
        break
    data, addr = s.recvfrom(4096)
    if data.decode() == "Error":
        print("An error again! Please try again")
    else:
        print("The phone number of " + message + " is " + data.decode())