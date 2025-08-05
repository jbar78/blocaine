# ATTENTION: la source de ce fichier ce trouve dans le répertoire "Target"
import pickle
debug_execbloc = False

class c_exebloc:
    """bloc executable"""
    def __init__(self, pbloc):
        if debug_execbloc: proc_name = "c_exec_bloc__init__: "
        if debug_execbloc: print (proc_name, " creation d'un bloc exécutable:   name=", pbloc.header['name'])
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
        print (proc_name, "ERROR id non trouve dans exebloc")
class c_exesubloc:
    """sous bloc executable"""
    def __init__(self, psubloc, pparent_ids):
        if debug_execbloc: proc_name = "c_exesubloc__init__: "
        if debug_execbloc: print (proc_name, " creation (uniquement l'entête) du bloc exécutable:   name=", psubloc.header['name'], "   (id=", psubloc.header['id'], ")")
        inputs = []
        outputs = []
        self.parent_ids = pickle.loads(pickle.dumps(pparent_ids))
        self.header = psubloc.header
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
        print (proc_name, "ERROR id non trouve dans exebloc")
        print (proc_name, "ERROR id non trouve dans exebloc: id=", pid)
        print (proc_name, "ERROR id non trouve dans exebloc: self=", self)
        print (proc_name, "ERROR id non trouve dans exebloc: self=", self.outputs)