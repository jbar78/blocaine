import socket
import threading
import pickle
from PARAM_NETWORK import *
from sharedata import clientsTCP
from c_exebloc import *
from exec import *
from compiled import *


def handle_clientTCP(client_socket, addr):
    def monitoring_user_bloc(pexebloc):
        def monitoring_user_bloc_io(pio):
            proc_name = "monitoring_user_bloc_io"
            #print (proc_name, f"boucle sublocs/pioss: ebloc_name={ebloc.header['name']}  input_name={pio['name']}")
            if 'monitoring_type' in pio:
                #print (proc_name, f"monitoring_type={pio['monitoring_type']},   monitoring_bloc={pio['monitoring_bloc_index']},   monitoring_io={pio['monitoring_io_index']}")
                i_bloc = pio['monitoring_bloc_index']
                i_io   = pio['monitoring_io_index']
                if pio['monitoring_type'] == "out":
                    #print (proc_name, f"monitoring_type={pio['monitoring_type']}, (copy output dans input)  monitoring_bloc={pio['monitoring_bloc_index']},   monitoring_io={pio['monitoring_io_index']}")
                    pio['var']   = pexebloc.sublocs[i_bloc].outputs[i_io]['var']
                    pio['valide']= pexebloc.sublocs[i_bloc].outputs[i_io]['valide']
                elif pio['monitoring_type'] == "in":
                    #print (proc_name, f"monitoring_type={pio['monitoring_type']}, (copy input dans output)   monitoring_bloc={pio['monitoring_bloc_index']},   monitoring_io={pio['monitoring_io_index']}")
                    pio['var']   = pexebloc.sublocs[i_bloc].inputs[i_io]['var']
                    pio['valide']= pexebloc.sublocs[i_bloc].inputs[i_io]['valide']
                else:
                    print ('proc_name', f"ERREUR: le USER est lié à un 'monitoring' de même type  type={pios['monitoring_type']}?")

        proc_name = "monitoring_user_bloc"
        #print (proc_name, " _____________________________________debut récupe monitoring io pour bloc USER")
        for ebloc in pexebloc.sublocs:
            #print (proc_name, f"boucle sublocs: ebloc_name={ebloc.header['name']}")
            for input in ebloc.inputs:
                #print (proc_name, f"boucle sublocs/inputs: ebloc_name={ebloc.header['name']}  input_name={input['name']}")
                monitoring_user_bloc_io(input)
            for output in ebloc.outputs:
                #print (proc_name, f"boucle sublocs/outputs: ebloc_name={ebloc.header['name']}  output_name={output['name']}")
                monitoring_user_bloc_io(output)
    def maj_forced_io (inputs_or_outputs):
        """ mise à jour de forced des inputs ou outputs """
        for ioput in inputs_or_outputs:
            print (proc_name, f"boucle sublocs/__puts: subloc_name={subloc.header['name']}  __put_name={ioput['name']}")
            if ioput['id'] == io_id:
                print(proc_name, f"input['id']==io_id  {ioput['id']}")
                if  cas == b"overwriting_value":
                    ioput['forced_value']= io_value
                elif cas == b"overwriting_validity":
                    print(proc_name, f"validity 'forced' in __put['id']={ioput['id']}")
                    ioput['forced_valide']= not ioput['forced_valide']
                elif cas == b"overwriting_start":
                    print(proc_name, f"add 'forced' in __put['id']={ioput['id']}")
                    ioput['forced_value']= ioput['var']
                    ioput['forced_valide']= ioput['valide']
                    ioput['forced']= True
                elif cas == b"overwriting_stop":
                    print(proc_name, f"del 'forced in __put['id']={ioput['id']}")
                    del ioput['forced']
                else: print (proc_name, "ERREUR: not start and no stop")

    global clientsTCP, list_compiled
    monitoring = None
    proc_name = "handle_clientTCP: "
    print ("clintsTCP.append")
    clientsTCP.append(addr)
    i=len(clientsTCP)-1
    txt_client = f" client[{i}] ({clientsTCP[i][0]}/{clientsTCP[i][1]}): "
    proc_name += txt_client
    try:
        while True:
            # receive and print client messages
            #print(proc_name, f"en attente d'un message")
            request = client_socket.recv(32768)
            #print(proc_name, f"réception d'un message!")
            #print(proc_name, f"Received: {request}")
            index =request.find(b':')
            #print(proc_name, f"index des deux points: {index}")
            cas = request[0:index]
            #print(proc_name, f"Received case: {cas}")
            #print(f"Received raw struct {request[index+1:]}")

            if (cas == b"transfer" or cas == b"execute") and index!= -1:
                curant_exebloc = pickle.loads(request[index+1:])

                bloc_name = curant_exebloc.header['name']
                print(proc_name, f"cas reconnu  (transfer ou exécute),     cas: {cas}")
                print(proc_name, f"ebloc reçu={bloc_name}")
                #print(proc_name, f"curant_exebloc={curant_exebloc}")
                compiled_load(curant_exebloc)
                if cas == b"execute":
                    print(proc_name, f"début d'exécution")
                    status = compiled_status()
                    for st in status:
                        if st['name'] == bloc_name:
                            print(proc_name, f"status de  <{bloc_name}> trouvé:  status={st}")
                            if "HotSwap" in st['orders']:
                                print(proc_name, f"HotSwap: trouvé")
                                hot_swap_exebloc(bloc_name)
                            elif "Run" in st['orders']:
                                if "ColdSwap" in st['orders']:
                                    print(proc_name, f"ColdSwap: trouvé")
                                    cold_swap_exebloc(bloc_name)
                                print(proc_name, f"Run: trouvé")
                                run_exebloc(bloc_name)
                            else:
                                print(proc_name, f"ERREUR: ni HotSwap, ni Run contenu dans status['orders']")

            elif cas == b"monitoring" and index!= -1:
                list_monitor = []
                #print(proc_name, f"cas N°2 reconnu  (monitoring)  cas: {cas}")
                #print(proc_name, f"  arborescence:{request[index+1:]}")
                monitoring = pickle.loads(request[index+1:])
                #print(proc_name, f"  monitoring['name']={monitoring['name']}")
                #print(proc_name, f"  monitoring['arbo_ids']={monitoring['arbo_ids']}")
                #print(proc_name, f" list_compiled: début de boucle")
                for ic, comp in enumerate(list_compiled):
                    #print(proc_name, f" list_compiled[{ic}].header['name']={comp.header['name']}")
                    if comp.header['name'] == monitoring['name'] and comp.header['master']:
                        monitoring_user_bloc (comp)
                        #print(proc_name, f" list_compiled[{ic}].header['name']={comp.header['name']} trouvée")
                        for subloc in comp.sublocs:
                            #print(proc_name, f" subloc.header['name']={subloc.header['name']} subloc.parent_ids={subloc.parent_ids}")
                            if subloc.parent_ids == monitoring['arbo_ids']:
                                #print(proc_name, f" parent_ids trouvée={subloc.parent_ids}")
                                list_monitor.append(subloc)
                if len(list_monitor) > 0:
                    response = pickle.dumps(list_monitor)
                else:
                    response = b"monitoring:not_found"
                client_socket.send(response)
            elif (cas == b"overwriting_start" or cas == b"overwriting_stop" or cas == b"overwriting_validity" or cas == b"overwriting_value") and index!= -1:
                print(proc_name, f"cas N°3 reconnu  OVERWRITING  cas: {cas}")
                print(proc_name, f"texte brut: {request}")
                print(proc_name, "-----------------------------------")
                textes = request.split(b':')
                print(proc_name, "textes=", textes)
                print(proc_name, "commande=textes[0]=", textes[0])
                tab_bloc_id = textes[1].split(b'=')
                print(proc_name, "txt bloc_id=tab_bloc_id[0]=", tab_bloc_id[0])
                print(proc_name, "txt bloc_id=tab_bloc_id[1]=", tab_bloc_id[1])
                bloc_id = int(tab_bloc_id[1])
                print(proc_name, f"bloc_id={bloc_id}")
                tab_io_id = textes[2].split(b'=')
                print(proc_name, "txt io_id=tab_io_id[0]=", tab_io_id[0])
                print(proc_name, "txt io_id=tab_io_id[1]=", tab_io_id[1])
                io_id = int(tab_io_id[1])
                if cas == b"overwriting_value":
                    tab_io_value = textes[3].split(b'=')
                    print(proc_name, "txt value=tab_io_value[0]=", tab_io_value[0])
                    print(proc_name, "txt value=tab_io_value[1]=", tab_io_value[1])
                    io_value = int(tab_io_value[1])

                print(proc_name, f"io_id={io_id}")
                print(proc_name, "-----------------------------------")
                for ic, comp in enumerate(list_compiled):
                    print(proc_name, f" list_compiled[{ic}].header['name']={comp.header['name']}")
                    if comp.header['name'] == monitoring['name'] and comp.header['master']:
                        #monitoring_user_bloc (comp)
                        print(proc_name, f" list_compiled[{ic}].header['name']={comp.header['name']} trouvée")
                        for subloc in comp.sublocs:
                            print(proc_name, f" subloc.header['name']={subloc.header['name']} subloc.parent_ids={subloc.parent_ids}")
                            if subloc.parent_ids == monitoring['arbo_ids']:
                                print(proc_name, f" parent_ids trouvée={subloc.parent_ids}")
                                if subloc.header['id'] == bloc_id:
                                    print(proc_name, f"==bloc_id  {subloc.header['id']}")
                                    maj_forced_io(subloc.inputs)
                                    maj_forced_io(subloc.outputs)

            elif cas == b"cas4" and index!= -1:
                print(proc_name, f"cas N°4 reconnu    cas: {cas}")
                #response = b"cas4"
            else:
                print(proc_name, f"Unknow Message Received: {request}")
                response = b"?"
                client_socket.send(response)
            # convert and send accept response to the client
            #response = "accepted"
            #client_socket.send(response)
    except Exception as e:
        print(proc_name, f"Error when hanlding client: {e}")
    finally:
        print (proc_name, "clientsTCP.remove")
        clientsTCP.remove(addr)
        client_socket.close()
        print(proc_name, f"Connection to client ({addr[0]}:{addr[1]}) closed")

def run_serverTCP():
    # create a socket object
    proc_name = "run_serverTCP: "
    try:
        print(proc_name, f"avant création soket d'écoute")
        serverTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(proc_name, f"après création soket d'écoute")
        # bind the socket to the host and port
        print(proc_name, f"avant bind sur soket d'écoute")
        #serverTCP.bind((PARAM_TCP_HOST_IP, PARAM_TCP_HOST_PORT )
        serverTCP.bind(('', PARAM_TCP_HOST_PORT ))
        print(proc_name, f"apès bind sur soket d'écoute")
        # listen for incoming connections
        print(proc_name, f"avant Listening on {PARAM_TCP_HOST_IP}:{PARAM_TCP_HOST_PORT }")
        serverTCP.listen()
        print(proc_name, f"après Listening on {PARAM_TCP_HOST_IP}:{PARAM_TCP_HOST_PORT }")

        while True:
            # accept a client connection
            #print(proc_name, f"avant .accept")
            client_socket, addr = serverTCP.accept()
            #print(proc_name, f"près .accept")
            print(proc_name, f"Accepted connection from {addr[0]}:{addr[1]}")
            # start a new thread to handle the client
            print(proc_name, f"create new thread for new client")
            thread = threading.Thread(target=handle_clientTCP, args=(client_socket, addr,))
            #print(proc_name, f"après .thread")
            thread.start()
    except Exception as e:
        print(proc_name, f"Error: {e}")
    finally:
        serverTCP.close()
        print(proc_name, f"Close")

