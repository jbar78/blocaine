# ATTENTION: la source de ce fichier ce trouve dans le répertoire "Target"

exec_level = 0
def trace_decal(plevel):
    """décalage pour print pour debug """
    decal =""
    for i in range (0, plevel):
        decal += "<--->"
    return decal
def trace_proc(psubloc, proc_name, plevel):
    proc_name = "level("+str(plevel)+")  "+trace_decal(plevel)+proc_name+": "
    bloc_name = "BLOC<"+psubloc.header['name']+">"
    if 'id' in psubloc.header:
        bloc_name = bloc_name+"  (id="+str(psubloc.header['id'])+") "
    return  bloc_name + proc_name
