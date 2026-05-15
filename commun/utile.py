# ATTENTION: la source de ce fichier ce trouve dans le répertoire "Target"


def cable_wires_counter (val):
    proc_name = "cable_wires_counter: "
    #print (proc_name, f"Paramètres: val={val},")
    if isinstance(val, tuple):
        #print (proc_name, f" avant call cable_wires_counter(): incrémentation")
        return_value =  cable_wires_counter(val[0])+1
        #print (proc_name, f" retourne ={return_value}")
        return return_value
    return 1


