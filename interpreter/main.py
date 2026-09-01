#! /usr/bin/python3
import threading
import socket
import pickle
from serverHTTP import *
from serverTCP import *
from compiled import *
from utile import get_local_ip
script_dir = os.path.dirname(os.path.abspath(__file__))  # Obtenir le répertoire du fichier courant
parent_dir = os.path.dirname(script_dir)                 # Remonter au dossier parent (projet/)
path_commun = os.path.join(parent_dir, "commun")         # Redescendre au répertoire "commun"
sys.path.append(path_commun)                             # Ajouter le répertoire "commun" au sys.path
from module_bloc_file import *
from c_exebloc import *
from exec import *
from threads import *
from threads import *
from sharedata import list_threads



def motor(pthread):
    """ moteur d'exécution """
    pthread['cycle_time'] = time.time() - pthread['start_time']
    pthread['start_time'] = time.time()
    proc_name= "motor: "
    #print (proc_name, "début-----Periode="+str(pthread['period'])+"(s)")
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
    pthread['min_max']['min'] = min(pthread['min_max']['min'], pthread['cycle_time'])
    pthread['min_max']['max'] = max(pthread['min_max']['max'], pthread['cycle_time'])
    



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


# démarrage automatique des blocs contenus dans le répertoire /startup
#print (f"Blocks defined in the startup configuration start automatically")
startup_blobcs = get_target_file_list(PARAM_CHEMIN_TARGET_STARTUP)
for bloc_name in startup_blobcs:
    #print (f"Block name={bloc_name}")
    file_name = PARAM_CHEMIN_TARGET_STARTUP+bloc_name
    #print (f"file name={file_name}")
    exebloc = read_bloc(file_name, use_file_name_as_name=False)
    print (f"Startup: start bloc <{exebloc.header['name']}>, build={exebloc.header['building'].strftime("%Y-%m-%d  %H:%M:%S")}")
    compiled_load(exebloc)
    run_exebloc(exebloc.header['name'])
print (f"startup complete")

print (f"Target is ready 😊")
