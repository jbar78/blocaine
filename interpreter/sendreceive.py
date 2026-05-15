import socket
import struct

import os
import sys
script_dir = os.path.dirname(os.path.abspath(__file__))  # Obtenir le répertoire du fichier courant
parent_dir = os.path.dirname(script_dir)                 # Remonter au dossier parent (projet/)
path_commun = os.path.join(parent_dir, "commun")         # Redescendre au répertoire "commun"
sys.path.append(path_commun)                             # Ajouter le répertoire "commun" au sys.path
from PARAM_NETWORK import *


def send_message(socket, data):
    proc_name = "send_message: "
    form = PARAM_TCP_MESS_HEADER_TYPE+str(len(data))+"s"
    #print (proc_name, f"format=<{form}>")
    header = len(data)
    #print(proc_name, f"header<{header}>,     data<{data}>\n")
    mess = struct.pack(form, header, data)
    #print(proc_name, f"mess <{mess}>         envoyé à {socket.host}:{socket.port}")
    send_all(socket, mess)

def send_all(socket, data):
    proc_name = "clientTCP.send_all: "
    if socket:
        socket.sendall(data)
        #print(proc_name, f"message <{data}> envoyé à {socket.host}:{socket.port}")
    #else:
        #print(proc_name, f"Erreur : Connexion non établie avec {socket.host}:{socket.port}")





def receive_message(client_socket): ########
    def receive_nbr(nbr):
        remaining = nbr
        mess_recu =b""
        while remaining > 0:
            recu = client_socket.recv(min(remaining, PARAM_TCP_BUFFER_SIZE))
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
    #print(proc_name, f"longueur du message utile reçu={len(mess_utile_recu)}")
    return mess_utile_recu

def receive_message22222(client_socket): ########
    proc_name = "receive_message: "
    header = client_socket.recv(PARAM_TCP_MESS_HEADER_SIZE)
    if len(header) < PARAM_TCP_MESS_HEADER_SIZE:
        raise ConnectionError("❌ERROR: TCP socket close because header length to short")
    #print(proc_name, f"réception de l'entête={header}")
    length = struct.unpack(PARAM_TCP_MESS_HEADER_TYPE, header)[0]
    #print(proc_name, f"longueur du message utile inscrite dans l'entête={length}")
    remaining = length
    mess_reçu =b""
    while remaining > 0:
        #reçu = client_socket.recv(min(length - len(mess_reçu), PARAM_TCP_BUFFER_SIZE))
        reçu = client_socket.recv(min(remaining, PARAM_TCP_BUFFER_SIZE))
        #print(proc_name, f"réception du message utile, len(reçu)={len(reçu)}")
        if not reçu:
            raise ConnectionError("❌ERROR: TCP socket close because message length to short")
        mess_reçu += reçu
        remaining -= len(reçu)
    return mess_reçu







def receive_messagexxx(): ########
    proc_name = "receive_message: "
    header = client_socket.recv(8)
    #print(proc_name, f"réception de l'entête={header}")
    (length,) = struct.unpack("!Q", header)
    #print(proc_name, f"longueur du message utile inscrite dans l'entête={length}")
    remaining = length
    mess_reçu =b""
    while remaining > 0:
        reçu = client_socket.recv(min(length, PARAM_TCP_BUFFER_SIZE))
        #print(proc_name, f"réception du message utile, len(reçu)={len(reçu)}")
        if not reçu:
            print(proc_name, "Connexion fermée avant réception complète.")
        mess_reçu += reçu
        remaining -= len(reçu)
    return mess_reçu
