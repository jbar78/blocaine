# ATTENTION: la source de ce fichier ce trouve dans le répertoire "Target"
import threading
import inspect
import time
import sys
import math
from PARAM_NAME_BLOC import *
from trace import trace_proc, exec_level
from c_exebloc import *


PARAM_TEXT_EXCEPTION = " EXCEPTION: so output(s) become unvalid"
debug_blocs = False

def recup_procedure(psubloc):
    proc_name = "recupe_procedure"
    """ ajout l'adresse de la procédure qui correspond au nom du bloc"""
    if   psubloc.header['name'] == PARAM_NAME_BLOC_DT:           procedure= c_exesubloc_dt
    elif psubloc.header['name'] == PARAM_NAME_BLOC_OUTPUT:       procedure= c_exesubloc_output
    elif psubloc.header['name'] == PARAM_NAME_BLOC_INPUT:        procedure= c_exesubloc_input
    elif psubloc.header['name'] == PARAM_NAME_BLOC_PREVIOUS:     procedure= c_exesubloc_previous
    elif psubloc.header['name'] == PARAM_NAME_BLOC_SELECT:       procedure= c_exesubloc_select
    elif psubloc.header['name'] == PARAM_NAME_BLOC_VALIDREAD:    procedure= c_exesubloc_validRead
    elif psubloc.header['name'] == PARAM_NAME_BLOC_VALIDWRITE:   procedure= c_exesubloc_validWrite
    elif psubloc.header['name'] == PARAM_NAME_BLOC_COMP:         procedure= c_exesubloc_comp
    elif psubloc.header['name'] == PARAM_NAME_BLOC_AND:          procedure= c_exesubloc_and
    elif psubloc.header['name'] == PARAM_NAME_BLOC_OR:           procedure= c_exesubloc_or
    elif psubloc.header['name'] == PARAM_NAME_BLOC_NOT:          procedure= c_exesubloc_not
    elif psubloc.header['name'] == PARAM_NAME_BLOC_EDGE:         procedure= c_exesubloc_edge
    elif psubloc.header['name'] == PARAM_NAME_BLOC_CABLIN:       procedure= c_exesubloc_cablin
    elif psubloc.header['name'] == PARAM_NAME_BLOC_CABLOUT:      procedure= c_exesubloc_cablout
    elif psubloc.header['name'] == PARAM_NAME_BLOC_ADD:          procedure= c_exesubloc_add
    elif psubloc.header['name'] == PARAM_NAME_BLOC_SUB:          procedure= c_exesubloc_sub
    elif psubloc.header['name'] == PARAM_NAME_BLOC_MULT:         procedure= c_exesubloc_mult
    elif psubloc.header['name'] == PARAM_NAME_BLOC_DIV:          procedure= c_exesubloc_div
    elif psubloc.header['name'] == PARAM_NAME_BLOC_MINMAX:       procedure= c_exesubloc_minmax
    elif psubloc.header['name'] == PARAM_NAME_BLOC_CONST_PI:     procedure= c_exesubloc_const_pi
    elif psubloc.header['name'] == PARAM_NAME_BLOC_MEMORY:       procedure= c_exesubloc_memory
    else:
        print (proc_name, " ERROR: function not defined for this bloc <"+psubloc.header['name']+">")
    return procedure


def c_exesubloc_output (pebloc, pieb, pio, pcounter):
    """ exécution du bloc OUTPUT (dans la boucler écurcive)"""
    global exec_level
    exec_level +=1
    cesubloc = pebloc.sublocs[pieb]
    if debug_blocs:
        trace_txt = trace_proc(cesubloc, inspect.currentframe().f_code.co_name, exec_level)
        print (trace_txt, "début OUTPUT les paramètres reçus sont: pieb=", pieb, ",   pio=", pio, ",   counter=", pcounter)
    if cesubloc.header['counter'] == pcounter:
        if debug_blocs: print (trace_txt, "  cesubloc['counter'] == pcounter: =", pcounter, "   (output[", pio, "] inchangée)")
    else:
        cesubloc.header['counter'] = pcounter
        if True: #try:
            pebloc.c_exebloc_recup_inputs(pieb, pcounter)
            cesubloc.c_exesubloc_validation_standard()

            cesubloc.outputs[0]['var'] = cesubloc.inputs[0]['var']
        else: #except:
            trace_txt = trace_proc(cesubloc, inspect.currentframe().f_code.co_name, exec_level)
            print (trace_txt, PARAM_TEXT_EXCEPTION)
            cesubloc.outputs[0]['valide'] = False
    if debug_blocs: print (trace_txt, " OUTPUT retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    exec_level -=1
    return cesubloc.outputs[pio]['var'], cesubloc.outputs[pio]['valide']
def c_exesubloc_input (pebloc, pieb, pio, pcounter):
    """ exécution du bloc INPUT (dans la boucler écurcive)"""
    global exec_level
    exec_level +=1
    cesubloc = pebloc.sublocs[pieb]
    if debug_blocs:
        trace_txt = trace_proc(cesubloc, inspect.currentframe().f_code.co_name, exec_level)
        print (trace_txt, "début INPUT les paramètres reçus sont: pieb=", pieb, ",   pio=", pio, ",   counter=", pcounter)
    if cesubloc.header['counter'] == pcounter:
        if debug_blocs: print (trace_txt, "  cesubloc['counter'] == pcounter: =", pcounter, "   (output[", pio, "] inchangée)")
    else:
        cesubloc.header['counter'] = pcounter
        try:
            pebloc.c_exebloc_recup_inputs(pieb, pcounter)
            cesubloc.c_exesubloc_validation_standard()

            cesubloc.outputs[0]['var'] = cesubloc.inputs[0]['var']

        except Exception as e:
            trace_txt = trace_proc(cesubloc, inspect.currentframe().f_code.co_name, exec_level)
            print (trace_txt, PARAM_TEXT_EXCEPTION)
            cesubloc.outputs[0]['valide'] = False
    if debug_blocs: print (trace_txt, " INPUT retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    exec_level -=1
    return cesubloc.outputs[pio]['var'], cesubloc.outputs[pio]['valide']
def c_exesubloc_previous (pebloc, pieb, pio, pcounter):
    """ exécution du bloc PREVIOUS (dans la boucler écurcive)"""
    global exec_level
    exec_level +=1
    cesubloc = pebloc.sublocs[pieb]
    if debug_blocs:
        trace_txt = trace_proc(cesubloc, inspect.currentframe().f_code.co_name, exec_level)
        print (trace_txt, "début PREVIOUS les paramètres reçus sont: pieb=", pieb, ",   pio=", pio, ",   counter=", pcounter)
    if cesubloc.header['counter'] == pcounter:
        if debug_blocs: print (trace_txt, "  cesubloc['counter'] == pcounter: =", pcounter, "   (output[", pio, "] inchangée)")
    else:
        cesubloc.header['counter'] = pcounter
        try:
            if pio != 1: # la pate (n-1) est morte! (elle ne gérére pas l'éxecution du bloc)
                pebloc.c_exebloc_recup_inputs(pieb, pcounter)
                cesubloc.c_exesubloc_validation_standard()

                cesubloc.outputs[0]['var'] = cesubloc.inputs[0]['var'] # n
                cesubloc.outputs[1]['var'] = cesubloc.inputs[0]['var'] # n-1
        except:
            trace_txt = trace_proc(cesubloc, inspect.currentframe().f_code.co_name, exec_level)
            print (trace_txt, PARAM_TEXT_EXCEPTION)
            cesubloc.outputs[0]['valide'] = False
    if debug_blocs: print (trace_txt, " PREVIOUS retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    exec_level -=1
    return cesubloc.outputs[pio]['var'], cesubloc.outputs[pio]['valide']
def c_exesubloc_select (pebloc, pieb, pio, pcounter):
    """ exécution du bloc SELECTION (dans la boucler écurcive)"""
    global exec_level
    exec_level +=1
    cesubloc = pebloc.sublocs[pieb]
    if debug_blocs:
        trace_txt = trace_proc(cesubloc, inspect.currentframe().f_code.co_name, exec_level)
        print (trace_txt, "début SELECT les paramètres sont: pieb=", pieb, ",   pio=", pio, ",   counter=", pcounter)
    INDEX_GATE=0
    INDEX_IF0=1
    INDEX_IF1=2
    if cesubloc.header['counter'] == pcounter:
        if debug_blocs: print (trace_txt, "  cesubloc['counter'] == pcounter: =", pcounter, "   (output[", pio, "] inchangée)")
    else:
        cesubloc.header['counter'] = pcounter
        try:
            pebloc.c_exebloc_recup_input (pieb, pcounter, INDEX_GATE)
            #if PARAM_DEBUG: print (trace_txt, "  GATE: input[0]['var']=", cesubloc.inputs[0]['var'], "   input[0]['valide']=", cesubloc.inputs[0]['valide'])
            if cesubloc.inputs[INDEX_GATE]['var']:
                pebloc.c_exebloc_recup_input (pieb, pcounter, INDEX_IF1)
                #if PARAM_DEBUG: print (trace_txt, "  IF1: input[2]['var']=", cesubloc.inputs[2]['var'], "   input[2]['valide']=", cesubloc.inputs[2]['valide'])
                cesubloc.outputs[0]['valide'] = cesubloc.inputs[INDEX_GATE]['valide'] and cesubloc.inputs[INDEX_IF1]['valide']
                cesubloc.outputs[0]['var']    = cesubloc.inputs[INDEX_IF1]['var']
            else:
                pebloc.c_exebloc_recup_input (pieb, pcounter, INDEX_IF0)
                #if PARAM_DEBUG: print (trace_txt, "  IF0: input[1]['var']=", cesubloc.inputs[1]['var'], "   input[1]['valide']=", cesubloc.inputs[1]['valide'])
                cesubloc.outputs[0]['valide'] = cesubloc.inputs[INDEX_GATE]['valide'] and cesubloc.inputs[INDEX_IF0]['valide']
                cesubloc.outputs[0]['var']    = cesubloc.inputs[INDEX_IF0]['var']
        except:
            trace_txt = trace_proc(cesubloc, inspect.currentframe().f_code.co_name, exec_level)
            print (trace_txt, PARAM_TEXT_EXCEPTION)
            cesubloc.outputs[0]['valide'] = False
    if debug_blocs: print (trace_txt, " SELECT retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    exec_level -=1
    return cesubloc.outputs[pio]['var'], cesubloc.outputs[pio]['valide']
def c_exesubloc_validRead (pebloc, pieb, pio, pcounter):
    """ exécution du bloc VALIDREAD: lecture de la validité"""
    global exec_level
    exec_level +=1
    cesubloc = pebloc.sublocs[pieb]
    if debug_blocs:
        trace_txt = trace_proc(cesubloc, inspect.currentframe().f_code.co_name, exec_level)
        print (trace_txt, "début VALIDREAD les paramètres sont: pieb=", pieb, ",   pio=", pio, ",   counter=", pcounter)
    if cesubloc.header['counter'] == pcounter:
        if debug_blocs: print (trace_txt, "  cesubloc['counter'] == pcounter: =", pcounter, "   (output[", pio, "] inchangée)")
    else:
        cesubloc.header['counter'] = pcounter
        try:
            pebloc.c_exebloc_recup_input (pieb, pcounter, 0)
            cesubloc.outputs[0]['var'] = cesubloc.inputs[0]['valide']
            cesubloc.outputs[0]['valide'] = True
        except:
            trace_txt = trace_proc(cesubloc, inspect.currentframe().f_code.co_name, exec_level)
            print (trace_txt, PARAM_TEXT_EXCEPTION)
            cesubloc.outputs[0]['valide'] = False
    if debug_blocs: print (trace_txt, " VALIREAD retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    exec_level -=1
    return cesubloc.outputs[pio]['var'], cesubloc.outputs[pio]['valide']
def c_exesubloc_validWrite (pebloc, pieb, pio, pcounter):
    """ exécution du bloc VALIDWRITE: surcharge la validité"""
    global exec_level
    exec_level +=1
    cesubloc = pebloc.sublocs[pieb]
    if debug_blocs:
        trace_txt = trace_proc(cesubloc, inspect.currentframe().f_code.co_name, exec_level)
        print (trace_txt, "début VALIWRITE les paramètres sont: pieb=", pieb, ",   pio=", pio, ",   counter=", pcounter)
    if cesubloc.header['counter'] == pcounter:
        if debug_blocs: print (trace_txt, "  cesubloc['counter'] == pcounter: =", pcounter, "   (output[", pio, "] inchangée)")
    else:
        cesubloc.header['counter'] = pcounter
        try:
            pebloc.c_exebloc_recup_inputs(pieb, pcounter)
            cesubloc.outputs[0]['var'] = cesubloc.inputs[0]['var']
            cesubloc.outputs[0]['valide'] = cesubloc.inputs[1]['var']
        except:
            trace_txt = trace_proc(cesubloc, inspect.currentframe().f_code.co_name, exec_level)
            print (trace_txt, PARAM_TEXT_EXCEPTION)
            cesubloc.outputs[0]['valide'] = False
    if debug_blocs: print (trace_txt, " VALIDWRITE retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    exec_level -=1
    return cesubloc.outputs[pio]['var'], cesubloc.outputs[pio]['valide']
def c_exesubloc_dt (pebloc, pieb, pio, pcounter):
    """ exécution du bloc DT retourne le temps de cycle (dans la boucler écurcive)"""
    global exec_level
    exec_level +=1
    cesubloc = pebloc.sublocs[pieb]
    if debug_blocs:
        trace_txt = trace_proc(cesubloc, inspect.currentframe().f_code.co_name, exec_level)
        print (trace_txt, "début DT les paramètres reçus sont: pieb=", pieb, ",   pio=", pio, ",   counter=", pcounter)
    if cesubloc.header['counter'] == pcounter:
        if debug_blocs:
            print (trace_txt, "  cesubloc['counter'] == pcounter: =", pcounter, "   (output[", pio, "] inchangée)")
    else:
        cesubloc.header['counter'] = pcounter
        try:
            if debug_blocs:
                print (trace_txt, "dt=", cesubloc.outputs[0]['var'])
                print (trace_txt, "t(n-1)=", cesubloc.outputs[1]['var'])
            cesubloc.outputs[0]['valide'] = cesubloc.outputs[1]['valide']
            cesubloc.outputs[1]['valide'] = True
            actual = time.time()
            dt = actual - cesubloc.outputs[1]['var']
            cesubloc.outputs[0]['var'] = dt
            cesubloc.outputs[1]['var'] = actual
        except:
            #print ("else False")
            trace_txt = trace_proc(cesubloc, inspect.currentframe().f_code.co_name, exec_level)
            print (trace_txt, PARAM_TEXT_EXCEPTION)
            cesubloc.outputs[pio]['valide'] = False
    if debug_blocs: print (trace_txt, " DT retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    exec_level -=1
    return cesubloc.outputs[pio]['var'], cesubloc.outputs[pio]['valide']
def c_exesubloc_comp (pebloc, pieb, pio, pcounter):
    """ exécution du bloc COMPARE (dans la boucler écurcive)"""
    global exec_level
    exec_level +=1
    cesubloc = pebloc.sublocs[pieb]
    if debug_blocs:
        trace_txt = trace_proc(cesubloc, inspect.currentframe().f_code.co_name, exec_level)
        print (trace_txt, "début COMP les paramètres sont: pieb=", pieb, ",   pio=", pio, ",   counter=", pcounter)
    if cesubloc.header['counter'] == pcounter:
        if debug_blocs: print (trace_txt, "  cesubloc['counter'] == pcounter: =", pcounter, "   (output[", pio, "] inchangée)")
    else:
        cesubloc.header['counter'] = pcounter
        try:
            pebloc.c_exebloc_recup_inputs(pieb, pcounter)
            cesubloc.c_exesubloc_validation_standard()

            cesubloc.outputs[0]['var'] = cesubloc.inputs[0]['var'] >  cesubloc.inputs[1]['var']
            cesubloc.outputs[1]['var'] = cesubloc.inputs[0]['var'] == cesubloc.inputs[1]['var']
            cesubloc.outputs[2]['var'] = cesubloc.inputs[0]['var'] <  cesubloc.inputs[1]['var']
        except:
            trace_txt = trace_proc(cesubloc, inspect.currentframe().f_code.co_name, exec_level)
            print (trace_txt, PARAM_TEXT_EXCEPTION)
            cesubloc.outputs[0]['valide'] = False
    if debug_blocs: print (trace_txt, " COMP retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    exec_level -=1
    return cesubloc.outputs[pio]['var'], cesubloc.outputs[pio]['valide']
def c_exesubloc_and (pebloc, pieb, pio, pcounter):
    """ exécution du bloc a et b (dans la boucle récurcive)"""
    global exec_level
    exec_level +=1
    cesubloc = pebloc.sublocs[pieb]
    if debug_blocs:
        trace_txt = trace_proc(cesubloc, inspect.currentframe().f_code.co_name, exec_level)
        print (trace_txt, "début AND les paramètres sont: pieb=", pieb, ",   pio=", pio, ",   counter=", pcounter)
    if cesubloc.header['counter'] == pcounter:
        if debug_blocs: print (trace_txt, "  cesubloc['counter'] == pcounter: =", pcounter, "   (output[", pio, "] inchangée)")
    else:
        cesubloc.header['counter'] = pcounter
        try:
            pebloc.c_exebloc_recup_inputs(pieb, pcounter)
            cesubloc.c_exesubloc_validation_standard()

            cesubloc.outputs[0]['var'] = cesubloc.inputs[0]['var'] and cesubloc.inputs[1]['var']
        except:
            trace_txt = trace_proc(cesubloc, inspect.currentframe().f_code.co_name, exec_level)
            print (trace_txt, PARAM_TEXT_EXCEPTION)
            cesubloc.outputs[0]['valide'] = False
    if debug_blocs: print (trace_txt, " AND retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    exec_level -=1
    return cesubloc.outputs[pio]['var'], cesubloc.outputs[pio]['valide']
def c_exesubloc_or (pebloc, pieb, pio, pcounter):
    """ exécution du bloc a ou b (dans la boucle récurcive)"""
    global exec_level
    exec_level +=1
    cesubloc = pebloc.sublocs[pieb]
    if debug_blocs:
        trace_txt = trace_proc(cesubloc, inspect.currentframe().f_code.co_name, exec_level)
        print (trace_txt, "début OR les paramètres sont: pieb=", pieb, ",   pio=", pio, ",   counter=", pcounter)
    if cesubloc.header['counter'] == pcounter:
        if debug_blocs: print (trace_txt, "  cesubloc['counter'] == pcounter: =", pcounter, "   (output[", pio, "] inchangée)")
    else:
        cesubloc.header['counter'] = pcounter
        try:
            pebloc.c_exebloc_recup_inputs(pieb, pcounter)
            cesubloc.c_exesubloc_validation_standard()

            cesubloc.outputs[0]['var'] = cesubloc.inputs[0]['var'] or cesubloc.inputs[1]['var']
        except:
            trace_txt = trace_proc(cesubloc, inspect.currentframe().f_code.co_name, exec_level)
            print (trace_txt, PARAM_TEXT_EXCEPTION)
            cesubloc.outputs[0]['valide'] = False
    if debug_blocs: print (trace_txt, " OR retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    exec_level -=1
    return cesubloc.outputs[pio]['var'], cesubloc.outputs[pio]['valide']
def c_exesubloc_not (pebloc, pieb, pio, pcounter):
    """ exécution du bloc a = non(b) (dans la boucler écurcive)"""
    global exec_level
    exec_level +=1
    cesubloc = pebloc.sublocs[pieb]
    if debug_blocs:
        trace_txt = trace_proc(cesubloc, inspect.currentframe().f_code.co_name, exec_level)
        print (trace_txt, "début NOT les paramètres sont: pieb=", pieb, ",   pio=", pio, ",   counter=", pcounter)
    if cesubloc.header['counter'] == pcounter:
        if debug_blocs: print (trace_txt, "  cesubloc['counter'] == pcounter: =", pcounter, "   (output[", pio, "] inchangée)")
    else:
        cesubloc.header['counter'] = pcounter
        try:
            pebloc.c_exebloc_recup_inputs(pieb, pcounter)
            cesubloc.c_exesubloc_validation_standard()

            cesubloc.outputs[0]['var'] = not cesubloc.inputs[0]['var']
        except:
            trace_txt = trace_proc(cesubloc, inspect.currentframe().f_code.co_name, exec_level)
            print (trace_txt, PARAM_TEXT_EXCEPTION)
            cesubloc.outputs[0]['valide'] = False
    if debug_blocs: print (trace_txt, " NOT retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    exec_level -=1
    return cesubloc.outputs[pio]['var'], cesubloc.outputs[pio]['valide']
def c_exesubloc_edge (pebloc, pieb, pio, pcounter):
    """ exécution du bloc détection de fronts (dans la boucle récurcive)"""
    global exec_level
    exec_level +=1
    cesubloc = pebloc.sublocs[pieb]
    if debug_blocs:
        trace_txt = trace_proc(cesubloc, inspect.currentframe().f_code.co_name, exec_level)
        print (trace_txt, "début EDGE les paramètres sont: pieb=", pieb, ",   pio=", pio, ",   counter=", pcounter)
    if cesubloc.header['counter'] == pcounter:
        if debug_blocs: print (trace_txt, "  cesubloc['counter'] == pcounter: =", pcounter, "   (output[", pio, "] inchangée)")
    else:
        cesubloc.header['counter'] = pcounter
        try:
            #print ("début EDGE les paramètres sont: pieb=", pieb, ",   pio=", pio, ",   counter=", pcounter)
            pebloc.c_exebloc_recup_input(pieb, pcounter, 0)
            cesubloc.c_exesubloc_validation_standard()

            cesubloc.outputs[0]['var'] = (cesubloc.inputs[1]['var'] and      cesubloc.inputs[0]['var']  and not cesubloc.outputs[1]['var'])\
                                      or (cesubloc.inputs[2]['var'] and (not cesubloc.inputs[0]['var']) and     cesubloc.outputs[1]['var'])
            cesubloc.outputs[1]['var'] = cesubloc.inputs[0]['var']
        except:
            trace_txt = trace_proc(cesubloc, inspect.currentframe().f_code.co_name, exec_level)
            print (trace_txt, PARAM_TEXT_EXCEPTION)
            cesubloc.outputs[0]['valide'] = False
    if debug_blocs: print (trace_txt, " EDGE retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    exec_level -=1
    return cesubloc.outputs[pio]['var'], cesubloc.outputs[pio]['valide']
def c_exesubloc_cablin (pebloc, pieb, pio, pcounter):
    """ exécution du bloc CABLIN (dans la boucle récurcive)"""
    global exec_level
    exec_level +=1
    cesubloc = pebloc.sublocs[pieb]
    if debug_blocs:
        trace_txt = trace_proc(cesubloc, inspect.currentframe().f_code.co_name, exec_level)
        print (trace_txt, "début CABLOUT les paramètres sont: pieb=", pieb, ",   pio=", pio, ",   counter=", pcounter)
    #print (proc_name, "début: input[0]: var=", cesubloc.inputs[0]['var'],   "valide=", cesubloc.inputs[0]['valide'])
    if cesubloc.header['counter'] == pcounter:
        if debug_blocs: print (trace_txt, "  cesubloc['counter'] == pcounter: =", pcounter, "   (output[", pio, "] inchangée)")
    else:
        cesubloc.header['counter'] = pcounter
        try:
            pebloc.c_exebloc_recup_inputs(pieb, pcounter)
            cesubloc.outputs[0]['valide'] = (cesubloc.inputs[0]['valide'], cesubloc.inputs[1]['valide'])
            cesubloc.outputs[0]['var']    = (cesubloc.inputs[0]['var'], cesubloc.inputs[1]['var'])
        except:
            trace_txt = trace_proc(cesubloc, inspect.currentframe().f_code.co_name, exec_level)
            print (trace_txt, PARAM_TEXT_EXCEPTION)
            cesubloc.outputs[0]['valide'] = False
    if debug_blocs: print (trace_txt, " CABLIN retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    exec_level -=1
    return cesubloc.outputs[pio]['var'], cesubloc.outputs[pio]['valide']
def c_exesubloc_cablout (pebloc, pieb, pio, pcounter):
    """ exécution du bloc CABLOUT (dans la boucler écurcive)"""
    global exec_level
    exec_level +=1
    cesubloc = pebloc.sublocs[pieb]
    if debug_blocs:
        trace_txt = trace_proc(cesubloc, inspect.currentframe().f_code.co_name, exec_level)
        print (trace_txt, "début CABLOUT les paramètres sont: pieb=", pieb, ",   pio=", pio, ",   counter=", pcounter)
    if cesubloc.header['counter'] == pcounter:
        if debug_blocs: print (trace_txt, "  cesubloc['counter'] == pcounter: =", pcounter, "   (output[", pio, "] inchangée)")
    else:
        cesubloc.header['counter'] = pcounter
        try:
            pebloc.c_exebloc_recup_inputs(pieb, pcounter)
            cesubloc.outputs[0]['var'] = cesubloc.inputs[0]['var'][0]
            cesubloc.outputs[1]['var'] = cesubloc.inputs[0]['var'][1]
            cesubloc.outputs[0]['valide'] = cesubloc.inputs[0]['valide'][0]
            cesubloc.outputs[1]['valide'] = cesubloc.inputs[0]['valide'][1]
        except:
            trace_txt = trace_proc(cesubloc, inspect.currentframe().f_code.co_name, exec_level)
            print (proc_name, PARAM_TEXT_EXCEPTION)
            cesubloc.outputs[0]['valide'] = False
    if debug_blocs: print (trace_txt, " CABLOUT retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    exec_level -=1
    return cesubloc.outputs[pio]['var'], cesubloc.outputs[pio]['valide']
def c_exesubloc_add (pebloc, pieb, pio, pcounter):
    """ exécution du bloc ADDITION (dans la boucler écurcive)"""
    global exec_level
    exec_level +=1
    cesubloc = pebloc.sublocs[pieb]
    if debug_blocs:
        trace_txt = trace_proc(cesubloc, inspect.currentframe().f_code.co_name, exec_level)
        print (trace_txt, "début ADD les paramètres reçus sont: pieb=", pieb, ",   pio=", pio, ",   counter=", pcounter)
    if cesubloc.header['counter'] == pcounter:
        if debug_blocs: print (trace_txt, "  cesubloc['counter'] == pcounter: =", pcounter, "   (output[", pio, "] inchangée)")
    else:
        cesubloc.header['counter'] = pcounter
        try:
            pebloc.c_exebloc_recup_inputs(pieb, pcounter)
            cesubloc.c_exesubloc_validation_standard()

            cesubloc.outputs[0]['var'] = cesubloc.inputs[0]['var'] + cesubloc.inputs[1]['var']
            if debug_blocs: print (trace_txt, " ADD retourne l'outout [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
        except:
            trace_txt = trace_proc(cesubloc, inspect.currentframe().f_code.co_name, exec_level)
            print (trace_txt, PARAM_TEXT_EXCEPTION)
            cesubloc.outputs[0]['valide'] = False
    if debug_blocs: print (trace_txt, " ADD retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    exec_level -=1
    return cesubloc.outputs[pio]['var'], cesubloc.outputs[pio]['valide']
def c_exesubloc_sub (pebloc, pieb, pio, pcounter):
    """ exécution du bloc SOUSTRACTION (dans la boucler écurcive)"""
    global exec_level
    exec_level +=1
    cesubloc = pebloc.sublocs[pieb]
    if debug_blocs:
        trace_txt = trace_proc(cesubloc, inspect.currentframe().f_code.co_name, exec_level)
        print (trace_txt, "début SUB les paramètres sont: pieb=", pieb, ",   pio=", pio, ",   counter=", pcounter)
    if cesubloc.header['counter'] == pcounter:
        if debug_blocs: print (trace_txt, "  cesubloc['counter'] == pcounter: =", pcounter, "   (output[", pio, "] inchangée)")
    else:
        cesubloc.header['counter'] = pcounter
        try:
            pebloc.c_exebloc_recup_inputs(pieb, pcounter)
            cesubloc.c_exesubloc_validation_standard()

            cesubloc.outputs[0]['var'] = cesubloc.inputs[0]['var'] - cesubloc.inputs[1]['var']
        except:
            trace_txt = trace_proc(cesubloc, inspect.currentframe().f_code.co_name, exec_level)
            print (trace_txt, PARAM_TEXT_EXCEPTION)
            cesubloc.outputs[0]['valide'] = False
    if debug_blocs: print (trace_txt, " SUB retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    exec_level -=1
    return cesubloc.outputs[pio]['var'], cesubloc.outputs[pio]['valide']
def c_exesubloc_mult (pebloc, pieb, pio, pcounter):
    """ exécution du bloc MULTIPLICATION (dans la boucler écurcive)"""
    global exec_level
    exec_level +=1
    cesubloc = pebloc.sublocs[pieb]
    if debug_blocs:
        trace_txt = trace_proc(cesubloc, inspect.currentframe().f_code.co_name, exec_level)
        print (trace_txt, "début MULT les paramètres sont: pieb=", pieb, ",   pio=", pio, ",   counter=", pcounter)
    if cesubloc.header['counter'] == pcounter:
        if debug_blocs: print (trace_txt, "  cesubloc['counter'] == pcounter: =", pcounter, "   (output[", pio, "] inchangée)")
    else:
        cesubloc.header['counter'] = pcounter
        try:
            pebloc.c_exebloc_recup_inputs(pieb, pcounter)
            cesubloc.c_exesubloc_validation_standard()

            cesubloc.outputs[0]['var'] = cesubloc.inputs[0]['var'] * cesubloc.inputs[1]['var']
        except:
            trace_txt = trace_proc(cesubloc, inspect.currentframe().f_code.co_name, exec_level)
            print (trace_txt, PARAM_TEXT_EXCEPTION)
            cesubloc.outputs[0]['valide'] = False
    if debug_blocs: print (trace_txt, " MUL retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    exec_level -=1
    return cesubloc.outputs[pio]['var'], cesubloc.outputs[pio]['valide']
def c_exesubloc_div (pebloc, pieb, pio, pcounter):
    """ exécution du bloc DIVISION (dans la boucler écurcive)"""
    global exec_level
    exec_level +=1
    cesubloc = pebloc.sublocs[pieb]
    if debug_blocs:
        trace_txt = trace_proc(cesubloc, inspect.currentframe().f_code.co_name, exec_level)
        print (trace_txt, "début DIV les paramètres sont: pieb=", pieb, ",   pio=", pio, ",   counter=", pcounter)
    if cesubloc.header['counter'] == pcounter:
        if debug_blocs: print (trace_txt, "  cesubloc['counter'] == pcounter: =", pcounter, "   (output[", pio, "] inchangée)")
    else:
        cesubloc.header['counter'] = pcounter
        try:
            pebloc.c_exebloc_recup_inputs(pieb, pcounter)
            cesubloc.c_exesubloc_validation_standard()

            cesubloc.outputs[0]['var'] = cesubloc.inputs[0]['var'] / cesubloc.inputs[1]['var']
        except:
            trace_txt = trace_proc(cesubloc, inspect.currentframe().f_code.co_name, exec_level)
            print (trace_txt, PARAM_TEXT_EXCEPTION)
            cesubloc.outputs[0]['valide'] = False
    if debug_blocs: print (trace_txt, " DIV retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    exec_level -=1
    return cesubloc.outputs[pio]['var'], cesubloc.outputs[pio]['valide']
def c_exesubloc_minmax (pebloc, pieb, pio, pcounter):
    """ exécution du bloc MINMAX (dans la boucler écurcive)"""
    global exec_level
    exec_level +=1
    cesubloc = pebloc.sublocs[pieb]
    if debug_blocs:
        trace_txt = trace_proc(cesubloc, inspect.currentframe().f_code.co_name, exec_level)
        print (trace_txt, "début MINMAX les paramètres sont: pieb=", pieb, ",   pio=", pio, ",   counter=", pcounter)
    if cesubloc.header['counter'] == pcounter:
        if debug_blocs: print (trace_txt, "  cesubloc['counter'] == pcounter: =", pcounter, "   (output[", pio, "] inchangée)")
    else:
        cesubloc.header['counter'] = pcounter
        try:
            pebloc.c_exebloc_recup_inputs(pieb, pcounter)
            cesubloc.c_exesubloc_validation_standard()

            cesubloc.outputs[0]['var'] = max(cesubloc.inputs[0]['var'], cesubloc.inputs[1]['var'])
            cesubloc.outputs[1]['var'] = min(cesubloc.inputs[0]['var'], cesubloc.inputs[1]['var'])
        except:
            trace_txt = trace_proc(cesubloc, inspect.currentframe().f_code.co_name, exec_level)
            print (trace_txt, PARAM_TEXT_EXCEPTION)
            cesubloc.outputs[0]['valide'] = False
    if debug_blocs: print (trace_txt, " MINMAX retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    exec_level -=1
    return cesubloc.outputs[pio]['var'], cesubloc.outputs[pio]['valide']
def c_exesubloc_const_pi (pebloc, pieb, pio, pcounter):
    """ exécution du bloc CONST_PI (dans la boucler écurcive)"""
    global exec_level
    exec_level +=1
    cesubloc = pebloc.sublocs[pieb]
    if debug_blocs:
        trace_txt = trace_proc(cesubloc, inspect.currentframe().f_code.co_name, exec_level)
        print (trace_txt, "début CONST_PI les paramètres sont: pieb=", pieb, ",   pio=", pio, ",   counter=", pcounter)
    if cesubloc.header['counter'] == pcounter:
        if debug_blocs: print (trace_txt, "  cesubloc['counter'] == pcounter: =", pcounter, "   (output[", pio, "] inchangée)")
    else:
        cesubloc.header['counter'] = pcounter
        try:
            cesubloc.outputs[0]['var'] =  math.pi
            cesubloc.outputs[0]['valide'] =  True
        except:
            trace_txt = trace_proc(cesubloc, inspect.currentframe().f_code.co_name, exec_level)
            print (trace_txt, PARAM_TEXT_EXCEPTION)
            cesubloc.outputs[0]['valide'] = False
    if debug_blocs: print (trace_txt, " CONST_PI retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    exec_level -=1
    return cesubloc.outputs[pio]['var'], cesubloc.outputs[pio]['valide']
def c_exesubloc_memory (pebloc, pieb, pio, pcounter):
    """ exécution du bloc bascule RS (dans la boucle récurcive)"""
    global exec_level
    SET=0
    RESET=1
    RESET_PRIORITAIRE=2
    exec_level +=1
    cesubloc = pebloc.sublocs[pieb]
    if debug_blocs:
        trace_txt = trace_proc(cesubloc, inspect.currentframe().f_code.co_name, exec_level)
        print (trace_txt, "début MEMORY les paramètres sont: pieb=", pieb, ",   pio=", pio, ",   counter=", pcounter)
    if cesubloc.header['counter'] == pcounter:
        if debug_blocs: print (trace_txt, "  cesubloc['counter'] == pcounter: =", pcounter, "   (output[", pio, "] inchangée)")
    else:
        cesubloc.header['counter'] = pcounter
        try:
            #print ("début MEMORY les paramètres sont: pieb=", pieb, ",   pio=", pio, ",   counter=", pcounter)
            pebloc.c_exebloc_recup_input(pieb, pcounter, 0)
            cesubloc.c_exesubloc_validation_standard()

            if cesubloc.inputs[SET]['var'] and (not cesubloc.inputs[RESET_PRIORITAIRE]['var'] or not cesubloc.inputs[RESET]['var']):
                cesubloc.outputs[0]['var'] = True

            if cesubloc.inputs[RESET]['var'] and (cesubloc.inputs[RESET_PRIORITAIRE]['var']  or not cesubloc.inputs[SET]['var']):
                cesubloc.outputs[0]['var'] = False
        except:
            trace_txt = trace_proc(cesubloc, inspect.currentframe().f_code.co_name, exec_level)
            print (trace_txt, PARAM_TEXT_EXCEPTION)
            cesubloc.outputs[0]['valide'] = False
    if debug_blocs: print (trace_txt, " MEMORY retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    exec_level -=1
    return cesubloc.outputs[pio]['var'], cesubloc.outputs[pio]['valide']
