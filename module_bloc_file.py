import os
import glob
import pickle
from PARAM import *

def set_dir(path):
    "directory change"
    os.chdir(path)
    return
def get_dir():
    "get curent word directory"
    return os.getcwd()
def get_list_of_bloc_file_name():
    "get all file name of avelable blocs"
    return glob.glob('*.bloc')
def get_name(chaine):
    dic={}
    #print "chaine",chaine
    trouve=chaine.find(".bloc")
    if trouve!=-1:
        dic['name']=chaine[0:trouve]
        #dic['version']=chaine[trouve+2:chaine.find(".bloc")]
    else:
        print ("ERREUR: dans GET_NAME la chaine <", chaine, "> n a pas ete trouvee")
    return dic
def get_list_of_bloc():
    "get all bloc name (and version) of avelable blocs"
    fnl=get_list_of_bloc_file_name()
    ret=[]
    for fn in fnl:
        ret.append(get_name(fn))
    return ret
def add_point_bloc_to_file_name (bloc_name):
    "create the complet file name"
    proc_name = "add_point_bloc_to_file: "
    #print (proc_name, "nom de fichier=",bloc_name+".bloc")
    return bloc_name+".bloc"
def write_bloc(pbloc):
    "backup a bloc"
    proc_name = "write_bloc: "
    print (proc_name, "début: name<"+pbloc.header['name']+">")
    #print (proc_name, "bloc=", pbloc)
    filen0 = add_point_bloc_to_file_name(pbloc.header['name'])
    filen = le_chemin(pbloc.header['name'], "system" in pbloc.header['key_word'])+filen0
    print (proc_name, "filename=", filen)
    file = open(filen, "wb")
    print (proc_name, "file=", file)
    pickle.dump(pbloc,file)
    #print (proc_name, "fin")
    file.close()
    print (proc_name, "fin: name<"+pbloc.header['name']+">")
    #return

def read_bloc(fname):
    "restore a bloc"
    global master, bloc
    proc_name =" read_bloc: "
    try:
        with open(fname, "rb") as file:
            #print (proc_name, "ouverture du fichier")
            bloc=pickle.load(file)
            #print (proc_name, "lecture du fichier")
    except FileNotFoundError:
        print (proc_name, "ERROR-----------file <", fname, ">can't be open")
        return None
    for i, elem in enumerate(bloc.sublocs):
        print ("{}     bloc[{}]= {}, id={}, --elem.header={}".format (proc_name, i, elem.header['name'], elem.header['id'], elem.header))
        for j, io in enumerate(elem.ios):
            print ( "{}                              ios[{}]= --{}".format (proc_name, j, io))
    file_name_with_extension = os.path.basename(fname) ###
    file = os.path.splitext(file_name_with_extension)
    name = file[0]
    #extension= file[1]
    bloc.header['name'] = name ###
    if bloc.header['structure_version'] != "2.0":
        print ("ERROR-----------------------------structure version of bloc file is not correct")
        return None
    #bloc['header']['name']={}
    #bloc['header']['name']=name
    return bloc
def le_chemin(name, psystem):
    if psystem: chemin = PARAM_CHEMIN_SYSTEM
    else: chemin= PARAM_CHEMIN_USER
    return chemin
def nom_complet_fichier(name, psystem):
    """ retour le nom du fichier avec cheim et extension"""
    proc_name = "nom_complet: "
    print (proc_name, "name=", name)
    if psystem: chemin = PARAM_CHEMIN_SYSTEM
    else: chemin= PARAM_CHEMIN_USER
    print (proc_name, "chemin=", chemin)
    retour = le_chemin(name, psystem)+name+".bloc"
    print (proc_name, "nom de fichier complet retourné=", retour)
    return retour
