# ATTENTION: la source de ce fichier ce trouve dans le répertoire "Target"
import pickle
import inspect
from trace import trace_proc, exec_level
debug_c_exe = False








class c_exebloc:
    """bloc executable"""
    def __init__(self, pbloc):
        if debug_c_exe: proc_name = "c_exec_bloc__init__: "
        if debug_c_exe: print (proc_name, " creation d'un bloc exécutable:   name=", pbloc.header['name'])
        sublocs = []
        self.header =pickle.loads(pickle.dumps(pbloc.header))
        self.header['AB']=""
        self.sublocs= sublocs
    def __repr__(self):
        chaine = "    Classs c_exec_bloc:\n"
        chaine = chaine  + "    -header=" + str(self.header) + "\n"
        for i, elem in enumerate(self.sublocs):
            chaine= chaine + "\n    -sublocs["+str(i)+"]=" + repr(self.sublocs[i])
        #for i, elem in enumerate(self.inputs):
        #    chaine= chaine + "  inputs=" + str(self.inputs[i]) + "\n"
        #for i, elem in enumerate(self.outputs):
        #    chaine= chaine + " outputs=" + str(self.outputs[i]) + "\n"
        return chaine  + "\n"
    def c_exebloc_find_index_exebloc (self, pid, pparent_ids):
        """ retourne l'index du sous-bloc executable correspondant à l'id du sous-bloc et aux id des parents"""
        proc_name = "c_exebloc_find_index_exebloc: "
        print (proc_name, "début: paramètres: pid=", pid, ",   pparent_ids[]=", pparent_ids)
        for i, esubloc in enumerate(self.sublocs):
            print (proc_name, "boucle esubloc["+str(i)+"]=    name<"+esubloc.header['name']+">  id<"+str(esubloc.header['id'])+">")
            if pparent_ids == esubloc.parent_ids:
                print (proc_name, " id lites équivalentes:    pparent_ids="+str(pparent_ids)+",   esubloc.parent_ids="+str(esubloc.parent_ids))
                if esubloc.header['id'] == pid:
                    print (proc_name, "id rechercher=", pid, "   index trouvé=", i)
                    return i
        print (proc_name, f"ERROR: id not found in exebloc,  id={pid}, ids={pparent_ids}")
    def c_exebloc_recup_input (self, pieb, pcounter, piei):
        """affecte un input en appelant le bloc parent (dans la boucle récurcive)"""
        def c_exebloc_recup_defaut (ptrace_txt, pinput):
            """affecte un input avec les valeurs par défaut"""
            global exec_level
            pinput['valide'] = True
            if 'local_defaut_value' in pinput:
                if debug_c_exe: print (ptrace_txt, ": récupération; local_defaut_value=", pinput['local_defaut_value'])
                pinput['var'] = pinput['local_defaut_value']
            elif 'defaut_value' in pinput:
                if debug_c_exe: print (ptrace_txt, ": récupération; defaut_value=", pinput['defaut_value'])
                pinput['var'] = pinput['defaut_value']
            else:
                return False
            return True
        cesubloc = self.sublocs[pieb]
        input = cesubloc.inputs[piei]
        if debug_c_exe:
            trace_txt = trace_proc(cesubloc, inspect.currentframe().f_code.co_name, exec_level)
            print (trace_txt, f"début RECUP_INPUT les paramètres sont:   piei={piei},   counter={pcounter}")
        if 'lien_bloc_index' in input and 'lien_output_index' in input:
            if debug_c_exe: print (trace_txt, "  il y a un lien pour cette input[", piei, "]:  name<", input['name'], ">")
            nesubloc = self.sublocs[input['lien_bloc_index']]
            input['var'], input['valide'] = nesubloc.header['procedure'](self, input['lien_bloc_index'], input['lien_output_index'], pcounter) #### appel procédure liée au bloc ####
        else:
            if debug_c_exe: print (trace_txt, "  il n'y a pas de lien pour cette input[" + str(piei) + "]:  name<" + input['name'] + ">")
            else: trace_txt = ":"
            defaut_value_found = c_exebloc_recup_defaut (trace_txt, input)
            if not defaut_value_found:
                trace_txt = trace_proc(cesubloc, inspect.currentframe().f_code.co_name, exec_level)
                print (trace_txt, ": ERROR: input[", piei, "] can not be found")
                input['valide'] = False
        if debug_c_exe: print (trace_txt, ": input[", piei, "], récupérée: var=", input['var'], "val=", input['valide'])
    def c_exebloc_recup_inputs (self, pieb, pcounter):
        """affecte les inputs en appelant les blocs parents (dans la boucle récurcive)"""
        cesubloc = self.sublocs[pieb]
        if debug_c_exe:
            trace_txt = trace_proc(cesubloc, inspect.currentframe().f_code.co_name, exec_level)
            #print (trace_txt, "début:")
        for index_input, input in enumerate(cesubloc.inputs):
            self.c_exebloc_recup_input (pieb, pcounter, index_input)
        #print (proc_name, "fin")
    def c_exebloc_filtre_blocs_userxxx (self):
        """retourne la liste des bocs USER ou SYSTEM"""
        user_list = []
        for esubloc in self.sublocs:
            if not 'system' in esubloc.header['key_word']:
                user_list.append(esubloc)
        return user_list



class c_exesubloc:
    """sous bloc executable"""
    def __init__(self, psubloc, pparent_ids):
        if debug_c_exe: proc_name = "c_exesubloc__init__: "
        if debug_c_exe: print (proc_name, " creation (uniquement l'entête) du bloc exécutable:   name=", psubloc.header['name'], "   (id=", psubloc.header['id'], ")")
        inputs = []
        outputs = []
        self.parent_ids = pickle.loads(pickle.dumps(pparent_ids))
        self.header =pickle.loads(pickle.dumps(psubloc.header))        #self.header = psubloc.header
        self.inputs= inputs
        self.outputs= outputs
    def __repr__(self):
        chaine = " Classs c_execsubloc:   <" + self.header['name'] + ">   (id=" + str(self.header['id']) + ")\n"
        chaine = chaine  + "        parent_ids[]:"
        #for i, id in enumerate(self.parent_ids):
        #    chaine= chaine + "  id["+str(i)+"]=" + str(self.parent_ids[i])+","
        chaine= chaine + str(self.parent_ids)
        chaine = chaine  + ")\n" #"   (levels="+str(len(self.parent_ids))+")\n"
        chaine = chaine  + "        header=" + str(self.header) + "\n"
        for i, elem in enumerate(self.inputs):
            chaine= chaine + "        inputs=" + str(self.inputs[i]) + "\n"
        for i, elem in enumerate(self.outputs):
            chaine= chaine + "        outputs=" + str(self.outputs[i]) + "\n"
        return chaine  #+ "\n"
    def c_exesubloc_find_index_exeoutput (self, pid):
        """ retourne l'index d'un output du sous-bloc executable correspondant à l'id de l'output"""
        proc_name = 'find_index_exeoutput'
        for i, output in enumerate(self.outputs):
            if output['id'] == pid:
                print (proc_name, "id rechercher=", pid, "   index trouvé=", i)
                return i
        print (proc_name, f"ERROR: id not found in exesubbloc: id={pid}")
    def c_exesubloc_user_type (self):
        """retourne VRAI si c'est un bloc USER (non SYSTEM)"""
        return not 'system' in self.header['key_word']






    def c_exesubloc_recup_last_outputxxxxxxx (self, pio):
        """retour l'ouput pio du bloc"""
        global exec_level
        #exec_level +=1
        #cesubloc = pebloc.sublocs[pieb]
        if debug_exec:
            trace_txt = trace_proc(self, inspect.currentframe().f_code.co_name, exec_level)
            print (trace_txt, f"début RECUP_LAST_OUTPUT les paramètres sont:  pio={pio}")
        #exec_level -=1
        if debug_exec: print (trace_txt, " LAST_OUTPUT retourne l'outout [", pio, "]: var=", self.outputs[pio]['var'], "val=", self.outputs[pio]['valide'])
        return self.outputs[pio]['var'], self.outputs[pio]['valide']



    def c_exesubloc_validation_standard(self):
        """ affecte de validités des sorties en fonction des validités des entrées
        une entrée invalide, inlalide toutes les sorties
        """
        proc_name = 'find_index_exeoutput'
        standard_val =True
        for input in self.inputs:
            if not input['valide']:
                standard_val = False
                break
        for output in self.outputs:
            output['valide'] = standard_val