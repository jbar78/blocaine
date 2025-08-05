import socket
from PARAM_NETWORK import *


#def run_clientTCP():
#    # create a socket object
#    clientTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#
#    server_ip = "192.168.122.224"  # replace with the server's IP address
#    server_port = 8000  # replace with the server's port number
#    # establish connection with server
#    try:
#        clientTCP.connect((server_ip, server_port))
#        print(f"TCP onnection to server established ):  server={server_ip}, port={server_port}")
#    except Exception as e:
#        print(f"Error: (TCP Connection to server) {e}")
#
#    try:
#        while True:
#            # get input message from user and send it to the server
#            msg = input("Enter message: ")
#            clientTCP.send(msg.encode("utf-8")[:1024])
#
#            # receive message from the server
#            response = clientTCP.recv(1024)
#            response = response.decode("utf-8")
#
#            # if server sent us "closed" in the payload, we break out of
#            # the loop and close our socket
#            if response.lower() == "closed":
#                break
#
#            print(f"Received: {response}")
#    except Exception as e:
#        print(f"Error: {e}")
#    finally:
#        # close client TCP socket (connection to the server)
#        clientTCP.close()
#        print("TCP Connection to server closed")

class TCPClient:
    def __init__(self):
        self.host = PARAM_TCP_HOST_IP # replace with the server's IP address
        self.port = PARAM_TCP_HOST_PORT  # replace with the server's port number
        self.socket = None

    def connect(self):
        proc_name = "connect: "
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((self.host, self.port))
            print(proc_name, f"Connexion TCP/IP établie avec {self.host}:{self.port}")
        except:
            print(proc_name, f"Connexion TCP/IP impossible {self.host}:{self.port}")
            self.close()

    def send_message(self, message):
        if self.socket:
            self.socket.sendall(message)
        else:
            print("Erreur : Connexion non établie")

    def receive_message(self, buffer_size=PARAM_TCP_BUFFER_SIZE):
        if self.socket:
            return self.socket.recv(buffer_size)
        else:
            print("Erreur : Connexion non établie")
            return None

    def close(self):
        if self.socket:
            self.socket.close()
            print("Connexion fermée")
        self.socket = None


