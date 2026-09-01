import os
import shutil
import glob
import pickle
from PARAM_NAME_BLOC import *
from PARAM_PATH import *

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
        print (f"❌ERROR: the string<{chaine}> has not be found in GET_NAME")
    return dic
def get_list_of_bloc():
    "get all bloc name (and version) of avelable blocs"
    fnl=get_list_of_bloc_file_name()
    ret=[]
    for fn in fnl:
        ret.append(get_name(fn))
    return ret
def add_point_bloc_to_file_name (pbloc_name, pstartup=False):
    "create the complet file name"
    proc_name = "add_point_bloc_to_file: "
    if pstartup:
        #print (proc_name, "nom de fichier=",pbloc_name+".bloc")
        return pbloc_name+".ebloc"
    else:
        #print (proc_name, "nom de fichier=",pbloc_name+".bloc")
        return pbloc_name+".bloc"
def write_bloc(pbloc, pstartup=False):
    "backup a bloc"
    proc_name = "write_bloc: "
    print (proc_name, "début: name<"+pbloc.header['name']+">")
    #print (proc_name, "bloc=", pbloc)
    if pstartup:
        txt_building = pbloc.header['building'].strftime("%Y-%m-%d__%H:%M:%S")
        filen0 = add_point_bloc_to_file_name(pbloc.header['name']+"__"+txt_building, pstartup)
        filen = PARAM_CHEMIN_TARGET_BUILD+filen0
    else:
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

def read_bloc(fname, use_file_name_as_name=True):
    "restore a bloc"
    proc_name =" read_bloc: "
    try:
        with open(fname, "rb") as file:
            #print (proc_name, "ouverture du fichier")
            local_bloc=pickle.load(file)
            #print (proc_name, "lecture du fichier")
    except FileNotFoundError:
        print (proc_name, "❌ERROR : file <", fname, ">can't be open")
        return None
    #print (proc_name, f"local_bloc.header['name']:{local_bloc.header['name']}")
    if use_file_name_as_name:
        #print (proc_name, f"use_file_name_as_name est VRAI")
        file_name_with_extension = os.path.basename(fname) ###
        file = os.path.splitext(file_name_with_extension)
        name = file[0]
        #extension= file[1]
        local_bloc.header['name'] = name ###
    if local_bloc.header['structure_version'] != "2.0":
        print (f"❌ERROR : structure version of bloc file is not correct, Version:{local_bloc.header['structure_version']}, expected:2.0")
        return None
    #print (proc_name, f"local_bloc.header['name']:{local_bloc.header['name']}")
    return local_bloc
def le_chemin(name, psystem):
    if psystem:
        chemin = PARAM_CHEMIN_DEV_SYSTEM
    else:
        chemin= PARAM_CHEMIN_DEV_USER
    return chemin


def nom_complet_fichier(name, psystem):
    """ retour le nom du fichier avec chemin et extension"""
    proc_name = "nom_complet: "
    print (proc_name, "name=", name)
    retour = le_chemin(name, psystem)+name+".bloc"
    print (proc_name, "nom de fichier complet retourné=", retour)
    return retour

def get_target_file_list(repertoire=PARAM_CHEMIN_TARGET_BUILD, extension=".ebloc"):
    """
    Retourne la liste des noms de fichiers avec l'extension '.ebloc' dans le répertoire spécifié.
    """
    try:
        # Vérifier si le répertoire existe
        if not os.path.isdir(repertoire):
            print(f"❌ERROR : Directory '{repertoire}' does'nt exist")
            return []
        # Lister tous les fichiers du répertoire
        fichiers = os.listdir(repertoire)
        # Filtrer les fichiers avec l'extension '.ebloc'
        fichiers_ebloc = [f for f in fichiers if f.endswith(extension)]
        return fichiers_ebloc
    except Exception as e:
        print(f"❌ERROR : file exception : {e}")
        return []

def move_file(source_dir: str, dest_dir: str, filename: str) -> bool:
    """
    Déplace un fichier d'un répertoire source vers un répertoire destination.
    Args:
        filename (str): Nom du fichier à déplacer (ex: "mon_fichier.txt").
        source_dir (str): Chemin du répertoire source (ex: "C:/dossier_source").
        dest_dir (str): Chemin du répertoire destination (ex: "C:/dossier_destination").
    Returns:
        bool: True si le déplacement a réussi, False en cas d'erreur.
    Exemples:
        >>> move_file("document.pdf", "C:/Téléchargements", "C:/Documents")
        True
    """
    proc_name = "move_file: "
    try:
        # 1. Vérifier que le fichier existe dans le répertoire source
        print
        source_path = os.path.join(source_dir, filename)
        if not os.path.exists(source_path):
            print(f"❌ ERROR: File '{filename}' does not exist '{source_dir}'.")
            return False

        # 2. Vérifier que le répertoire destination existe, sinon le créer
        os.makedirs(dest_dir, exist_ok=True)

        # 3. Construire le chemin de destination
        dest_path = os.path.join(dest_dir, filename)

        # 4. Vérifier que le fichier n'existe pas déjà dans la destination
        if os.path.exists(dest_path):
            print(f"⚠️ Avertissement : File '{filename}' already exist in'{dest_dir}'. It will be overwritten.")
            # Option : Renommer le fichier existant (ex: "fichier (1).txt")
            base, ext = os.path.splitext(filename)
            counter = 1
            while os.path.exists(dest_path):
                dest_path = os.path.join(dest_dir, f"{base} ({counter}){ext}")
                counter += 1

        # 5. Déplacer le fichier
        shutil.move(source_path, dest_path)
        print(f"✅ File '{filename}' successfully moved from '{source_dir}' to '{dest_dir}'.")
        return True

    except PermissionError:
        print(f"❌ ERROR: Permission denied. Check directory access rights.")
    except shutil.Error as e:
        print(f"❌ ERROR: while moving : {e}")
    except Exception as e:
        print(f"❌ ERROR: exception: {e}")

    return False