import socket
import struct
from PARAM_NETWORK import *



class clientTCP:
    def __init__(self):
        proc_name = "clientTCP.__init__: "
        self.socket = None
        self.nb_receive= 0
        print (proc_name, "initialisation de l'objet <clientTCP>")
        print (proc_name, f"socket=<{self.socket}>")

    def connect(self, address, port):
        proc_name = "clientTCP.connect: "
        self.host = address
        self.port = port
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print (proc_name, "socket créée!")
            print (proc_name, f"socket=<{self.socket}>")
            self.socket.connect((self.host, self.port))
            print(proc_name, f"Connexion TCP/IP établie avec {self.host}:{self.port}")
        except:
            print(proc_name, f"Connexion TCP/IP impossible {self.host}:{self.port}")
            self.close()
        print (proc_name, f"socket=<{self.socket}>")


    def send_message(self, data):
        proc_name = "clientTCP.send_message: "
        form = "!Q"+str(len(data))+"s"
        #print (proc_name, f"format=<{form}>")
        header = len(data)
        #print(proc_name, f"header<{header}>,     data<{data}>\n")
        mess = struct.pack(form, header, data)
        #print(proc_name, f"mess <{mess}>         envoyé à {self.host}:{self.port}")
        self.send_all(mess)

    def send_all(self, data):
        proc_name = "clientTCP.send_all: "
        if self.socket:
            self.socket.sendall(data)
            #print(proc_name, f"message <{data}> envoyé à {self.host}:{self.port}")
        else:
            print(proc_name, f"Erreur : Connexion non établie avec {self.host}:{self.port}")


    def receive_message(self, buffer_size=PARAM_TCP_BUFFER_SIZE): ########
        proc_name = "receive_message: "
        header = self.socket.recv(8)
        #print(proc_name, f"réception de l'entête={header}")
        (length,) = struct.unpack("!Q", header)
        #print(proc_name, f"longeur du message utile inscrite dans l'entête={length}")
        remaining = length
        mess_reçu =b""
        while remaining > 0:
            reçu = self.socket.recv(min(length, PARAM_TCP_BUFFER_SIZE))
            #print(proc_name, f"réception du message utile, len(reçu)={len(reçu)}")
            if not reçu:
                print(proc_name, "Connexion fermée avant réception complète.")
            mess_reçu += reçu
            remaining -= len(reçu)
        return mess_reçu

    def receive_messagexxx(self, buffer_size=PARAM_TCP_BUFFER_SIZE):
        proc_name = "clientTCP.receive_message: "
        self.nb_receive += 1
        if self.socket:
            print(proc_name, f"message[{self.nb_receive}] reçu de {self.host}:{self.port}")
            return self.socket.recv(buffer_size)
        else:
            print(proc_name, f"Erreur : Connexion non établie avec {self.host}:{self.port}")
            return None

    def close(self):
        proc_name = "clientTCP.close: "
        #if self.socket:
        self.socket.close()
        print(proc_name, f"Connexion avec ({self.host}:{self.port})")
        self.socket = None



