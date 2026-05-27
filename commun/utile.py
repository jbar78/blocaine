# ATTENTION: la source de ce fichier ce trouve dans le répertoire "Target"
import socket


def cable_wires_counter (val):
    proc_name = "cable_wires_counter: "
    #print (proc_name, f"Paramètres: val={val},")
    if isinstance(val, tuple):
        #print (proc_name, f" avant call cable_wires_counter(): incrémentation")
        return_value =  cable_wires_counter(val[0])+1
        #print (proc_name, f" retourne ={return_value}")
        return return_value
    return 1

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Cette connexion n'a pas besoin d'être établie réellement
        s.connect(('10.254.254.254', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP
