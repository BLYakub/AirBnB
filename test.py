from tkinter import *
from customers import *
from offers import *
from functions import *
from socket import *
import _thread

# Main TCP socket that runs the connection between the client and server
sock = socket(AF_INET,SOCK_STREAM)
sock.connect(("localhost",55000))

# UDP socket
udp_sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP) # UDP
udp_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
udp_sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
udp_sock.bind(("", 55554))

# The cliet recieves the current date that the server sends, 
# whether it is the real date or the date that the admin set
current_date = sock.recv(1024).decode()

root = Tk()

# Creates class object for all of the client functions
win = functions(root, sock, current_date)

# Function that gets the new time that the admin changed to
def get_time_change():
    global win
    while True:
        data, addr = udp_sock.recvfrom(1024)
        data = data.decode()

        if not data:
            break
        if "change_date" in data:
            data = data.split(':')
            win.current_date = data[1]

# Runs the function in a thread so that it can recieve the new date while the client functions still run
_thread.start_new_thread(get_time_change, ())
root.mainloop()
