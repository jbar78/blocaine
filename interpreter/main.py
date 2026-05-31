#! /usr/bin/python3
import threading
import socket
from serverHTTP import *
from serverTCP import *
from utile import get_local_ip

script_dir = os.path.dirname(os.path.abspath(__file__))  # Obtenir le répertoire du fichier courant
parent_dir = os.path.dirname(script_dir)                 # Remonter au dossier parent (projet/)
path_commun = os.path.join(parent_dir, "commun")         # Redescendre au répertoire "commun"
sys.path.append(path_commun)                             # Ajouter le répertoire "commun" au sys.path
from threads import *
from sharedata import list_threads



def motor(pthread):
    """ moteur d'exécution """
    pthread['start_time'] = time.time()
    proc_name= "motor: "
    #print (proc_name, "début-----Periode="+str(pthread['period'])+"(s)")
    pthread['idle_time'] = pthread['start_time'] - pthread['end_time']
    #_________________________________début
    FLAG_PRINT_OUTPUTS = False
    FLAG_PRINT_EN_COURS = False
    if 'list_exe' in pthread:
        #print (proc_name, "_debut_______________________________________________________________________________ periode="+str(pthread['period'])+"(s)")
        for i, exe in enumerate(pthread['list_exe']):
            if exe['run']:
                cesubloc = exe['exebloc'].sublocs[exe['iesubloc']]
                #print (proc_name, "BLOC<"+exe['exebloc'].header['name']+"> /"+exe['exebloc'].header['AB'])
                #print (proc_name, "début---Periode="+str(pthread['period'])+"(s)---Counter="+str(pthread['counter']))
                result = cesubloc.header['procedure'](exe['exebloc'], exe['iesubloc'], 0, pthread ) #### appel procédure liée au bloc ####

        if FLAG_PRINT_OUTPUTS:
            for i, exe in enumerate(pthread['list_exe']):
                bloc_name = exe['exebloc'].header['name']               # nom du bloc exécuté
                AB   = exe['exebloc'].header['AB']                      # version du bloc exécuté
                ibo  = exe['iesubloc']                                  # index du subloc "output"
                ido  = exe['exebloc'].sublocs[ibo].header['id']         # ID du subloc "output"
                oname = exe['exebloc'].sublocs[ibo].outputs[0]['name']           # nom de l'entreé du bloc OUTPUT
                var  = exe['exebloc'].sublocs[ibo].outputs[0]['var']     # valeur de l'ouptput
                val  = exe['exebloc'].sublocs[ibo].outputs[0]['valide']  # validité de l'ouptput
                if exe['run']:
                    if not FLAG_PRINT_EN_COURS:
                        FLAG_PRINT_EN_COURS = True
                        print (proc_name, "début---Periode="+str(pthread['period'])+"(s)---Counter="+str(pthread['counter']))
                    print (proc_name, "        Periode="+str(pthread['period'])+"(s)---Counter="+str(pthread['counter'])+"--- BLOC<"+bloc_name+"> /"+AB+"    résultat de l'OUTPUT name=<"+oname+"> (id="+str(ido)+")  bloc["+str(ibo)+"]:   valide="+str(val)+"   var=",var)
            if FLAG_PRINT_EN_COURS:
                print (proc_name, "fin-----Periode="+str(pthread['period'])+"(s)\n")
    #print (proc_name, "fin-----Periode="+str(pthread['period'])+"(s)\n")
    pthread['counter'] += 1
    #_________________________________fin
    #print (proc_name, "fin-----Periode="+str(pthread['period'])+"(s)\n")
    pthread['end_time'] = time.time()
    pthread['run_time'] = pthread['end_time'] - pthread['start_time']
    pthread['cycle_time'] = pthread['idle_time'] + pthread['run_time']
    pthread['min_max']['min'] = min(pthread['min_max']['min'], pthread['cycle_time'])
    pthread['min_max']['max'] = max(pthread['min_max']['max'], pthread['cycle_time'])
    pthread['load_%'] = 100*(pthread['run_time'] / pthread['idle_time'])




import time
# Création des évènements périodiques (arment du motor d'exécution)
for i, thread in enumerate(list_threads):
    thread['min_max']['min'] = 99999999999
    thread['min_max']['max'] = -99999999999
    thread['thread'] = Intervallometre(motor, [thread])
    thread['thread'].setDaemon(True)
    thread['thread'].start()
time.sleep (0.3)

# Démarrez le serveur HTTP dans un thread séparé
serverHTTP_thread = threading.Thread(target=run_serverHTTP)
serverHTTP_thread.start()


# Démarrez le serveur TCP dans un thread séparé (communication avec éditeur de bloc)
serverTCP_thread = threading.Thread(target=run_serverTCP)
serverTCP_thread.start()



# affiche des adresse ipv4 disponible
time.sleep (0.5)
print (f"Target IP address: {get_local_ip()}")
print (f"Target is ready 😊")

