import socket
import struct

import os
import sys
script_dir = os.path.dirname(os.path.abspath(__file__))  # Obtenir le répertoire du fichier courant
parent_dir = os.path.dirname(script_dir)                 # Remonter au dossier parent (projet/)
path_commun = os.path.join(parent_dir, "commun")         # Redescendre au répertoire "commun"
sys.path.append(path_commun)                             # Ajouter le répertoire "commun" au sys.path
from PARAM_NETWORK import *
from PARAM_TARGET_ADDRESS import PARAM_TCP_TARGET_IP



class clientTCP:
    def __init__(self):
        proc_name = "clientTCP.__init__: "
        self.socket = None
        self.nb_receive= 0
        #print (proc_name, "create clientTCP object")
        #print (proc_name, f"socket=<{self.socket}>")

    def connect(self, address, port):
        proc_name = "clientTCP.connect: "
        self.host = address
        self.port = port
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #print (proc_name, "socket créée!")
            #print (proc_name, f"socket=<{self.socket}>")
            self.socket.connect((self.host, self.port))
            print(proc_name, f"Connection established with Target {self.host}:{self.port}")
        except:
            print(proc_name, f"❌Connection with Target {self.host}:{self.port} refused")
            self.close()
        #print (proc_name, f"socket={self.socket}")


    def send_message(self, data):
        proc_name = "clientTCP.send_message: "
        form = PARAM_TCP_MESS_HEADER_TYPE+str(len(data))+"s"
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
            print(proc_name, f"❌Error : Connexion not establiched with {self.host}:{self.port}")





    def receive_message(self): ########
        def receive_nbr(nbr):
            remaining = nbr
            mess_recu =b""
            while remaining > 0:
                recu = self.socket.recv(min(remaining, PARAM_TCP_BUFFER_SIZE))
                #print(proc_name, f"réception du message utile, len(reçu)={len(recu)}")
                #if not recu:
                #    #raise ConnectionError("❌ERROR: TCP socket close because message length to short")
                #    print (proc_name, f"waiting message: length to short, remaining={remaining}")
                mess_recu += recu
                remaining -= len(recu)
            return mess_recu
        proc_name = "receive_message: "
        header = receive_nbr(PARAM_TCP_MESS_HEADER_SIZE)
        length = struct.unpack(PARAM_TCP_MESS_HEADER_TYPE, header)[0]
        #print(proc_name, f"longueur du message utile inscrite dans l'entête={length}")
        mess_utile_recu = receive_nbr(length)
        #print(proc_name, f"longueur du message utile: entête={length} VS reçu={len(mess_utile_recu)}")
        return mess_utile_recu




    def receive_message33333(self):
        proc_name = "receive_message: "
        header = self.socket.recv(PARAM_TCP_MESS_HEADER_SIZE)
        if len(header) < PARAM_TCP_MESS_HEADER_SIZE:
            raise ConnectionError("❌ERROR: TCP socket close because header length to short")
        #print(proc_name, f"réception de l'entête={header}")
        length = struct.unpack(PARAM_TCP_MESS_HEADER_TYPE, header)[0]
        #print(proc_name, f"longueur du message utile inscrite dans l'entête={length}")
        remaining = length
        mess_reçu =b""
        while remaining > 0:
            #reçu = self.socket.recv(min(length - len(mess_reçu), PARAM_TCP_BUFFER_SIZE))
            reçu = self.socket.recv(min(remaining, PARAM_TCP_BUFFER_SIZE))
            #print(proc_name, f"réception du message utile, len(reçu)={len(reçu)}")
            if not reçu:
                raise ConnectionError("❌ERROR: TCP socket close because message length to short")
            mess_reçu += reçu
            remaining -= len(reçu)
        return mess_reçu

    """
    def receive_messagexxxx(self, buffer_size=PARAM_TCP_BUFFER_SIZE): ########
        proc_name = "receive_message: "
        header = self.socket.recv(8)
        #print(proc_name, f"réception de l'entête={header}")
        (length,) = struct.unpack("!Q", header)
        #print(proc_name, f"longueur du message utile inscrite dans l'entête={length}")
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

    def receive_messagexxx(self, buffer_size=PARAM_TCP_BUFFER_SIZE): #xxx
        proc_name = "clientTCP.receive_message: "
        self.nb_receive += 1
        if self.socket:
            print(proc_name, f"message[{self.nb_receive}] reçu de {self.host}:{self.port}")
            return self.socket.recv(buffer_size)
        else:
            print(proc_name, f"❌Error : Connexion not establiched with {self.host}:{self.port}")
            return None
    """


    def close(self):
        proc_name = "clientTCP.close: "
        if self.socket!=None:
            self.socket.close()
            print(proc_name, f"Fermeture connexion ({self.host}:{self.port})")
            self.socket = None
        else:
            print(proc_name, f"❌Error : can not close onnection ({self.host}:{self.port}): allready close ")



