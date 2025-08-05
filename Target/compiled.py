from PARAM_NAME_BLOC import *
from sharedata import list_compiled, list_threads

def compiled_find_master(bloc_name, master):
    """retourne index du master ou non master"""
    global list_compiled
    proc_name = "compiled_find_master: "
    if master:
        txt_param = "recherche MASTER"
    else:
        txt_param = "recherche PENDING"
    print (proc_name, "début", txt_param)
    for i, cb in enumerate(list_compiled):
        print (proc_name, f"boucle   i={i}")
        if cb.header['name']  == bloc_name:
            print (proc_name, f"même nom={bloc_name}")
            if master == cb.header['master']:
                print (proc_name, f"même master={master}")
                if master:
                    txt= "master"
                else:
                    txt = "No master"
                print(proc_name,  txt+f" MASTER trouvé dans list_compiled (index={i})  le bloc<{cb.header['name']}> /{cb.header['AB']}")
                return True, i
    print (proc_name, "non trouvé   ", txt_param)
    return False, -1
def compiled_status():
    """retourne les status des shift A et B"""
    global list_compiled
    list_status=[]
    def status_texte (pbloc):
        if find_running_bloc (pbloc.header['name'], pbloc.header['AB']):
            return "Running"
        else:
            if pbloc.header['master']:
                return "Ready"
            else:
                return "Pending"
        return "error"

    def orders(sta):
        """retourne les ordres disponible"""
        proc_name = "orders: "
        #print (proc_name, f"début")
        list_orders=[]
        if sta['status_A']=="Ready" or sta['status_B']=="Ready":
            #print (proc_name, f"Aredy ou Bready =run")
            list_orders.append("Run")
        if sta['status_A']=="Running" or sta['status_B']=="Running":
            #print (proc_name, f"Aruning ou Brunning =stop")
            list_orders.append("Stop")
            list_orders.append("Initialize")
        if (sta['status_A']=="Pending" and sta['status_B']=="Ready") or (sta['status_A']=="Ready" and sta['status_B']=="Pending"):
            #print (proc_name, f"(Apending ET Bready) OU (Aready ET Bpending) =ColdSawp")
            list_orders.append("ColdSwap")
        if (sta['status_A']=="Running" and sta['status_B']=="Pending") or (sta['status_A']=="Pending" and sta['status_B']=="Running") :
            #print (proc_name, f"(Aruning ET Bpending) OR (Apending ET Brunning) =HotSwap")
            list_orders.append("HotSwap")
        if sta['status_A']!="Running" and sta['status_B']!="Running":
            #print (proc_name, f"A/running ET B/running =delete")
            list_orders.append("Delete")
        html_orders =""
        for ordr in list_orders:
            html_orders += f"&nbsp;<a href='/order:{ordr}:{sta['name']}'>{ordr}</a>&nbsp;"
        sta['orders']=html_orders

    proc_name = "compiled_status: "
    #print (proc_name, f"début")
    for i,cb in enumerate(list_compiled):
        #print (proc_name, f"boucle1   i={i}")
        trouvé = -1
        for j, cs in enumerate(list_status):
            if cb.header['name'] == cs['name']:
                trouvé = j
                break
        if trouvé > -1:
            #if cd.header['AB']=="A"
            key = "status_"+cb.header['AB']
            list_status[trouvé][key] = status_texte(cb)
        else:
            status={}
            status['name']=cb.header['name']
            status['AB']=cb.header['AB']
            key = "status_"+cb.header['AB']
            list_status.append(status)
            status[key] = status_texte(cb)
    for ls in list_status:
        if not 'status_A' in ls: ls['status_A'] = "..."
        if not 'status_B' in ls: ls['status_B'] = "..."
    #print (proc_name, f"status sans orders={list_status}")
    for cs in list_status:
        orders(cs)
    #print (proc_name, f"status avec orders={list_status}")
    return list_status

def compiled_load(curant_exebloc):
    """Charge le bloc exécutable reçu dans list_compiled"""
    global list_compiled
    proc_name = "compiled_load: "
    print (proc_name, "début")
    #trouvé = False
    #for i, cb in enumerate(list_compiled):
    #   if (cb.header['name']  == curant_exebloc.header['name']) and not master:
    #       print(proc_name,  f"remplace dans list_compiled (index={i})  le bloc<{cb.header['name']}> /{cb.header['AB']}")
    #       curant_exebloc.header['AB'] = cb.header['AB']
    #       list_compiled[i] = curant_exebloc # mise à jour du bloc compilé
    #       trouvé = True
    master, imaster   = compiled_find_master(curant_exebloc.header['name'], master=True)
    pending, ipending = compiled_find_master(curant_exebloc.header['name'], master=False)

    #if not trouvé:
    if pending: # si le bloc est "pending" le mettre à jour
        curant_exebloc.header['master'] = False
        curant_exebloc.header['AB'] = list_compiled[ipending].header['AB']
    else:# si le bloc n'est pas "pending" il faut en ajouter un
        print(proc_name,  f"ajout en fin de list_compiled")
        if master: # si le bloc est "ready" ou "running" 
            print(proc_name,  f"C'est un bloc master  shift={list_compiled[imaster].header['AB']}")
            if list_compiled[imaster].header['AB'] == "A":
                curant_exebloc.header['AB'] = "B"
            else:
                curant_exebloc.header['AB'] = "A"
            curant_exebloc.header['master'] = False
            print(proc_name,  f"à ajout bloc={curant_exebloc.header['name']} Shift={curant_exebloc.header['AB']} master={curant_exebloc.header['master']}")
        else:
            curant_exebloc.header['AB'] = "A"
            curant_exebloc.header['master'] = True
        print(proc_name,  f"ajout à list_compiled[{ipending}]  bloc={curant_exebloc.header['name']}  /{curant_exebloc.header['AB']}  master={curant_exebloc.header['master']}")
    delete_exebloc_AB(curant_exebloc.header['name'], curant_exebloc.header['AB'])
    list_compiled.append(curant_exebloc) # ajout du bloc compilé

    for ebloc in list_compiled:
        if curant_exebloc.header['name'] == ebloc.header['name'] and curant_exebloc.header['AB'] == ebloc.header['AB']:
            print (proc_name, "boucle des sousbloc de: BLOC=",ebloc.header['name']," /",ebloc.header['AB'])
            for ib, subloc in enumerate(ebloc.sublocs):
                print (proc_name, "     subobj: name=",subloc.header['name'])
                #if 'subloc_id' in omemo:
                if subloc.header['name'] == PARAM_NAME_BLOC_OUTPUT:
                    #print (proc_name,     " output trouvé: name=", subloc.header['name'], ", id=", subloc.header['id'])
                    if 'event_id' in subloc.header:
                        index = find_thread_index(subloc.header['event_id'])
                        dic={}
                        dic['exebloc'] = ebloc
                        dic['iesubloc'] = ib
                        dic['run'] = False
                        list_threads[index]['list_exe'].append(dic)

    print(proc_name,  f"fin: list_compiled,  len={len(list_compiled)}")
def find_thread_index(pthread_id):
    """ retour l'index du thread correspondant à l'ID"""
    global list_threads
    proc_name = "find_thread_index"
    #print (proc_name, ":  liste des threads: (ID à trouver=", pthread_id, ")")
    for i, thread in enumerate(list_threads):
        #print (proc_name, ":   - thread[", i, "] name=", thread['name'], "  période=", thread['period'], "   compteur=", thread['counter'])
        if pthread_id == thread['id']:
            #print (proc_name, "index retouné=", i)
            return i
    print (proc_name, " WARNING thread ID<"+str(pthread_id)+"> non trouvé")
    return None
def find_running_bloc(pname, pAB):
    """ retour vrai si le bloc "name" de la version AB tourne """
    global list_threads
    proc_name = "find_running_bloc: "
    #print (proc_name, "  BLOC recherché:  name=", pname, "   version=", pAB)
    for ith, thread in enumerate(list_threads):
        #print (proc_name, "   - thread[", ith, "] name=", thread['name'], "  période=", thread['period'], "   compteur=", thread['counter'])
        for i, exe in enumerate(thread['list_exe']):
            if pname == exe['exebloc'].header['name'] and  pAB == exe['exebloc'].header['AB']  :
                #print (proc_name, "  trouvé: index thread=", ith, "    index list_exe=", i, "  run=",exe['run'])
                if exe['run']:
                    return True
    print (proc_name, " BLOC<"+pname+"> /"+pAB+" non trouvé")
    return False
def initialize(pname, pAB):
    """initialise le bloc exécutable reçu dans list_compiled"""
    global list_compiled
    proc_name = "initialize: "
    print (proc_name, f"début: paramètres: name={pname},  AB={pAB}")
    for ebloc in list_compiled:
        if pname == ebloc.header['name'] and pAB == ebloc.header['AB']:
            print (proc_name, " boucle: BLOC=",ebloc.header['name']," /",ebloc.header['AB'])
            for subloc in ebloc.sublocs:
                print (proc_name, " boucle récup subobj: name=",subloc.header['name'])
                for index_output, output in enumerate(subloc.outputs):
                    print (proc_name, "  récup Memory: output["+str(index_output)+"] name<"+output['name']+">")
                    if 'initial_value' in output:
                        output['var'] = output['initial_value']
                        output['valide'] = True
def running(pname, pAB):
    """ Arrête l'execution de la version courante (non pAB)
    ajoute les subbloc OUTPUT à exécuté dans la structure list_threads et démarre la version pAB """
    global list_compiled, list_threads
    proc_name = "running: "
    print (proc_name, "paramètres:  name<"+pname+">    AB="+pAB)
    for thread in list_threads:
        for exe in thread['list_exe']:
            if pname == exe['exebloc'].header['name'] and pAB != exe['exebloc'].header['AB']:
                exe['run'] = False
            if pname == exe['exebloc'].header['name'] and pAB == exe['exebloc'].header['AB']:
                exe['run'] = True

def swaping(pname, pAB):
    """ Arrête l'execution de la version courante et demarre la version pAB
    ajoute les subbloc OUTPUT à exécuté dans la structure list_threads """
    """utlilisation de fonction de captation des paramètre: capture_add_event"""
    global list_compiled, list_threads
    list_omemos= []
    proc_name = "running: "
    print (proc_name, "paramètres:  name<"+pname+">    AB="+pAB)
    #______________________________stop the bloc NON pAB
    for thread in list_threads:
        for exe in thread['list_exe']:
            if pname == exe['exebloc'].header['name'] and pAB != exe['exebloc'].header['AB']:
                exe['run'] = False
    #____________________________récup les valeurs mémorisées du bloc NON pAB
    for ebloc in list_compiled:
        if pname == ebloc.header['name'] and pAB != ebloc.header['AB']:
            print (proc_name, " boucle récup: BLOC=",ebloc.header['name']," /",ebloc.header['AB'])
            for subloc in ebloc.sublocs:
                print (proc_name, " boucle récup subobj: name=",subloc.header['name'])
                if 'system' in subloc.header['key_word']:
                    print (proc_name, " récup Memory: c'est un subloc SYSTEM name=",subloc.header['name'])
                    for index_output, output in enumerate(subloc.outputs):
                        print (proc_name, "  récup Memory: output["+str(index_output)+"] name<"+output['name']+">")
                        if 'memory' in output:
                            omemo = {}
                            print (proc_name, "  récup Memory: output["+str(index_output)+"] name<"+output['name']+"> Memory trouvée")
                            omemo['subloc_id'] = subloc.header['id']
                            omemo['parent_ids'] = subloc.parent_ids
                            omemo['output_id'] = subloc.outputs[index_output]['id']
                            omemo['var'] = subloc.outputs[index_output]['var']
                            omemo['valide'] = subloc.outputs[index_output]['valide']
                            print (proc_name, "  omemo=", omemo, "récup var=", omemo['var'], "dans /",ebloc.header['AB'])
                            list_omemos.append(omemo)
                    #omemo['subloc_id'] = subloc.header['id']
                    #omemo['parent_ids'] = subloc.parent_ids
                    #omemo['output_id'] = subloc.outputs[ioutput]['id']
                    #omemo['var'] = subloc.outputs[ioutput]['var']
                    #omemo['valide'] = subloc.outputs[ioutput]['valide']
                    #print (proc_name, "  omemo=", omemo, "récup var=", omemo['var'], "dans /",ebloc.header['AB'])
                    #list_omemos.append(omemo)
    print (proc_name, "Liste des outpout mémorisé (nb element="+str(len(list_omemos))+") récupéré dans"+ebloc.header['AB']+":")
    for i, m in enumerate(list_omemos):
        print (proc_name, "    récup dans /"+ebloc.header['AB']+"   list_omemos["+str(i)+"]=", m)
    #____________________________copie les valeurs mémorisées vers le bloc pAB
    for ebloc in list_compiled:
        if pname == ebloc.header['name'] and pAB == ebloc.header['AB']:
            print (proc_name, "boucle des sousbloc de: BLOC=",ebloc.header['name']," /",ebloc.header['AB'])
            for ib, subloc in enumerate(ebloc.sublocs):
                print (proc_name, "     subobj: name=",subloc.header['name'])
                #if 'subloc_id' in omemo:
                for omemo in list_omemos:
                    if subloc.header['id'] == omemo['subloc_id'] and subloc.parent_ids == omemo['parent_ids']:
                        index_output = subloc.c_exesubloc_find_index_exeoutput (omemo['output_id'])
                        subloc.outputs[index_output]['var']    = omemo['var']
                        subloc.outputs[index_output]['valide'] = omemo['valide']
                        print (proc_name, "  omemo=", omemo, "copié var=", omemo['var'], " dans /",ebloc.header['AB'])

    #______________________________start the bloc pAB
    for thread in list_threads:
        for exe in thread['list_exe']:
            if pname == exe['exebloc'].header['name'] and pAB == exe['exebloc'].header['AB']:
                exe['run'] = True




def stoping(pname, pibo, pAB):
    """ Arrête l'execution de la version courante"""
    global list_threads
    #print (proc_name, "paramètres:  name<"+pname+">    AB="+pAB)
    #for thread in list_threads:
    #    for exe in thread['list_exe']:
    #        if pname == exe['exebloc'].header['name'] and pAB != exe['exebloc'].header['AB']:
    #            exe['run'] = False
    proc_name="stopping: "
    print (proc_name, " paramètres:  name="+pname+"  output index="+str(pibo)+"   version="+pAB)
    for ith, thread in enumerate(list_threads):
        print (proc_name, ":   - thread["+str(ith)+"] name="+thread['name']+"  période="+str(thread['period'])+"   compteur="+str(thread['counter']))
        for i, exe in enumerate(thread['list_exe']):
            print (proc_name, "  - thread["+str(ith)+"]: list_exe["+str(i)+"]  execbloc name="+exe['exebloc'].header['name'])
            print (proc_name, "  - thread["+str(ith)+"]: list_exe["+str(i)+"]   iesbloc="+str(exe['iesubloc']))
            print (proc_name, "  - thread["+str(ith)+"]: list_exe["+str(i)+"]   run="+str(exe['run']))
            if exe['exebloc'].header['name'] == pname\
                    and (exe['iesubloc'] == pibo or pibo == None)\
                    and exe['exebloc'].header['AB'] == pAB\
                    and exe['run']:
                print (proc_name, " run="+str(exe['run'])+"   >>> STOPPING")
                exe['run'] = False
def cold_swap_exebloc(pname):
    global list_compiled
    proc_name = "cold_sawp_exebloc: "
    print (proc_name, "début,   bloc name=", pname)
    master, imaster   = compiled_find_master(pname, master=True)
    pending, ipending = compiled_find_master(pname, master=False)
    list_compiled[ipending].header['master'] = True
    list_compiled[imaster].header['master'] = False
def hot_swap_exebloc(pname):
    global list_compiled
    proc_name = "hot_sawp_exebloc: "
    print (proc_name, "début,   bloc name=", pname)
    master, imaster   = compiled_find_master(pname, master=True)
    pending, ipending = compiled_find_master(pname, master=False)
    list_compiled[ipending].header['master'] = True
    list_compiled[imaster].header['master'] = False
    master, imaster   = compiled_find_master(pname, master=True)
    swaping(list_compiled[imaster].header['name'], list_compiled[imaster].header['AB'])
def run_exebloc(pname):
    proc_name = "run_exebloc: "
    print (proc_name, "début,   bloc name=", pname)
    ls = compiled_status()
    for sta in ls:
        if sta['name'] == pname:
            AB = ""
            if sta['status_A'] == "Ready": AB = "A"
            if sta['status_B'] == "Ready": AB = "B"
            if AB != "":
                initialize(pname, AB)
                running   (pname, AB)
            else:
                print (proc_name, "ERREUR  bloc name=", pname, "ni A, ni B, n'est READY")
def stop_exebloc(pname):
    proc_name = "stop_exebloc: "
    print (proc_name, "début,   bloc name=", pname)
    ls = compiled_status()
    for sta in ls:
        if sta['name'] == pname:
            if sta['status_A'] == "Running": stoping(pname, None, "A")
            if sta['status_B'] == "Running": stoping(pname, None, "B")
def delete_exebloc_AB(pname, pAB):
    """ supprime un shifts spécifique du bloc """
    global list_compiled, list_threads
    proc_name = "delete_exebloc_AB: "
    print (proc_name, f"début,   bloc name={pname}  /{pAB}")
    for  cb in list_compiled.copy():
        if cb.header['name'] == pname and cb.header['AB'] == pAB :
            list_compiled.remove(cb)
    for  thread in list_threads.copy():
        for exe in thread['list_exe'].copy():
            if exe['exebloc'].header['name'] == pname and exe['exebloc'].header['AB'] == pAB:
                thread['list_exe'].remove(exe)
def delete_exebloc(pname):
    """ supprime les shifts du bloc """
    global list_compiled, list_threads
    proc_name = "delete_exebloc: "
    delete_exebloc_AB(pname, "A")
    delete_exebloc_AB(pname, "B")
def init_exebloc(pname):
    proc_name = "init_exebloc: "
    print (proc_name, "début,   bloc name=", pname)
    ls = compiled_status()
    for sta in ls:
        if sta['name'] == pname:
            if sta['status_A'] == "Running": initialize(pname, "A")
            if sta['status_B'] == "Running": initialize(pname, "B")

def print_exeblocs():
    global list_compiled
    proc_name = "print_exeblocs: "
    print (proc_name, "Liste des blocs compilés:   nb="+str(len(list_compiled)))
    for ebloc in list_compiled:
        print (proc_name, "   - EBLOC: name<"+ebloc.header['name']+">   /"+ebloc.header['AB'])
        print (ebloc)
def print_threads():
    global list_threads
    proc_name = "print_threads: "
    print (proc_name, "\n")
    print (proc_name, "Liste des thread:   nb="+str(len(list_threads)))
    for thread in list_threads:
        print (proc_name, f"   - THREAD: name<{thread['name']}>   id={thread['id']}   period={thread['period']}   counter={thread['counter']}")
        print (proc_name, "List_exe:   nb="+str(len(thread['list_exe'])))
        for exe in thread['list_exe']:
            print (proc_name, f"list_exe: bloc name<{exe['exebloc'].header['name']}>  /{exe['exebloc'].header['AB']},   OUTPUT name<{exe['exebloc'].sublocs[exe['iesubloc']].header['name']}>  OUTPUT id<{exe['exebloc'].sublocs[exe['iesubloc']].header['id']}>  input name<{exe['exebloc'].sublocs[exe['iesubloc']].inputs[0]['name']}>,  run={exe['run']}")
            #print (proc_name, f"list_exe: index OUTPUT={exe['iesubloc']}>")
            #print (proc_name, f"list_exe: run={exe['run']}")
            #print (proc_name, f"list_exe: bloc name<{exe['exebloc'].sublocs[exe['iesubloc']].header['name']}> ")
