#! /usr/bin/python3
import threading
from serverHTTP import *
from serverTCP import *
from threads import *
from sharedata import list_threads



def motor(pthread):
    pthread['start_time'] = time.time()
    proc_name= "motor: "
    #print (proc_name, "début-----Periode="+str(pthread['period'])+"(s)")
    pthread['idle_time'] = pthread['start_time'] - pthread['end_time']
    #_________________________________début
    FLAG_PRINT_OUTPUTS = False
    flag_print_debut = False
    if 'list_exe' in pthread:
        #print (proc_name, "_debut_______________________________________________________________________________ periode="+str(pthread['period'])+"(s)")
        for i, exe in enumerate(pthread['list_exe']):
            if exe['run']:
                cesubloc = exe['exebloc'].sublocs[exe['iesubloc']]
                #print (proc_name, "BLOC<"+exe['exebloc'].header['name']+"> /"+exe['exebloc'].header['AB'])
                result = cesubloc.header['procedure'](exe['exebloc'], exe['iesubloc'], 0, pthread['counter'] ) #### appel procédure liée au bloc ####

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
                    if not flag_print_debut:
                        flag_print_debut = True
                        print (proc_name, "début---Periode="+str(pthread['period'])+"(s)---Counter="+str(pthread['counter']))
                    print (proc_name, "        Periode="+str(pthread['period'])+"(s)---Counter="+str(pthread['counter'])+"--- BLOC<"+bloc_name+"> /"+AB+"    résultat de l'OUTPUT name=<"+oname+"> (id="+str(ido)+")  bloc["+str(ibo)+"]:   valide="+str(val)+"   var=",var)
            if flag_print_debut:
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



# Démarrez le serveur HTTP dans un thread séparé
serverHTTP_thread = threading.Thread(target=run_serverHTTP)
serverHTTP_thread.start()

# Démarrez le serveur TCP: communication avec éditeur de bloc
serverTCP_thread = threading.Thread(target=run_serverTCP)
serverTCP_thread.start()


import time

# Création des évènements périodiques (arment du motor d'exécution)
for i, thread in enumerate(list_threads):
    thread['min_max']['min'] = 99999999999
    thread['min_max']['max'] = -99999999999
    thread['thread'] = Intervallometre(motor, [thread])
    thread['thread'].setDaemon(True)
    thread['thread'].start()

