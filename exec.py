# ATTENTION: la source de ce fichier ce trouve dans le répertoire "Target"
import threading
import inspect
import time
import sys
import math
from PARAM_NAME_BLOC import *
from c_exebloc import *
from sharedata import list_threads


PARAM_TEXT_EXCEPTION = " EXCEPTION: so output(s) become unvalid"

def recup_procedure(psubloc):
    proc_name = "recupe_procedure"
    """ ajout l'adresse de la procédure qui correspond au nom du bloc"""
    if   psubloc.header['name'] == PARAM_NAME_BLOC_TIME:         procedure= c_exesubloc_time
    elif psubloc.header['name'] == PARAM_NAME_BLOC_DT:           procedure= c_exesubloc_dt
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
    elif psubloc.header['name'] == PARAM_NAME_BLOC_DELAY:        procedure= c_exesubloc_delay
    elif psubloc.header['name'] == PARAM_NAME_BLOC_CLOCK:        procedure= c_exesubloc_clock
    elif psubloc.header['name'] == PARAM_NAME_BLOC_LIMIT:        procedure= c_exesubloc_limit
    elif psubloc.header['name'] == PARAM_NAME_BLOC_DIFFERENCIAL: procedure= c_exesubloc_differencial
    elif psubloc.header['name'] == PARAM_NAME_BLOC_INTEGRATOR:   procedure= c_exesubloc_integrator
    elif psubloc.header['name'] == PARAM_NAME_BLOC_FILTER_FO:    procedure= c_exesubloc_filter_FO
    elif psubloc.header['name'] == PARAM_NAME_BLOC_INPUT_OUTPUT: procedure= c_exesubloc_input_output
    else:
        print (proc_name, " ERROR: function not defined for this bloc <"+psubloc.header['name']+">")
    return procedure


def c_exesubloc_output (pebloc, pieb, pio, pthread):
    """ exécution du bloc OUTPUT (dans la boucler écurcive)"""
    cesubloc = pebloc.sublocs[pieb]
    #print ("<OUTPUT> les paramètres reçus sont: pieb=", pieb, ",   pio=", pio, ",   counter=", pthread['counter'])
    if cesubloc.header['counter'] == pthread['counter']:
        pass
        #print ("cesubloc['counter'] == pthread['counter']: =", pthread['counter'], "   (output[", pio, "] inchangée)")
    else:
        cesubloc.header['counter'] = pthread['counter']
        try:
            pebloc.c_exebloc_recup_input(pieb, pthread, 0)
            #cesubloc.c_exesubloc_validation_standard()

            cesubloc.outputs[0]['var']    = cesubloc.inputs[0]['var']
            cesubloc.outputs[0]['valide'] = cesubloc.inputs[0]['valide']
        except:
            #print ("<OUTPUT>", PARAM_TEXT_EXCEPTION)
            cesubloc.outputs[0]['valide'] = False
        cesubloc.c_exesubloc_overwriting_outputs()
    #print ("<OUTPUT> retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    return cesubloc.outputs[pio]['var'], cesubloc.outputs[pio]['valide']
def c_exesubloc_input (pebloc, pieb, pio, pthread):
    """ exécution du bloc INPUT (dans la boucler écurcive)"""
    cesubloc = pebloc.sublocs[pieb]
    #print ("début INPUT les paramètres reçus sont: pieb=", pieb, ",   pio=", pio, ",   counter=", pthread['counter'])
    if cesubloc.header['counter'] == pthread['counter']:
        pass
        #print ("cesubloc['counter'] == pthread['counter']: =", pthread['counter'], "   (output[", pio, "] inchangée)")
    else:
        cesubloc.header['counter'] = pthread['counter']
        try:
            pebloc.c_exebloc_recup_input(pieb, pthread, 0)
            #cesubloc.c_exesubloc_validation_standard()
            cesubloc.outputs[0]['var']    = cesubloc.inputs[0]['var']
            cesubloc.outputs[0]['valide'] = cesubloc.inputs[0]['valide']
        except:
            #print ("<INPUT>", PARAM_TEXT_EXCEPTION)
            cesubloc.outputs[0]['valide'] = False
        cesubloc.c_exesubloc_overwriting_outputs()
    #print ("<INPUT> retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    return cesubloc.outputs[pio]['var'], cesubloc.outputs[pio]['valide']
def c_exesubloc_previous (pebloc, pieb, pio, pthread):
    """ exécution du bloc PREVIOUS (dans la boucler écurcive)"""
    cesubloc = pebloc.sublocs[pieb]
    #print ("<PREVIOUS> les paramètres reçus sont: pieb=", pieb, ",   pio=", pio, ",   counter=", pthread['counter'])
    if pio != 1: # la pate (n-1) est morte! (elle ne gérére pas l'éxecution du bloc)
        if cesubloc.header['counter'] == pthread['counter']:
            pass
            #print ("cesubloc['counter'] == pthread['counter']: =", pthread['counter'], "   (output[", pio, "] inchangée)")
        else:
            cesubloc.header['counter'] = pthread['counter']
            try:
                pebloc.c_exebloc_recup_input(pieb, pthread, 0)
                cesubloc.c_exesubloc_validation_standard()
                cesubloc.outputs[0]['var'] = cesubloc.inputs[0]['var'] # n
                cesubloc.outputs[1]['var'] = cesubloc.inputs[0]['var'] # n-1
            except:
                #print ("<PREVIOUS>", PARAM_TEXT_EXCEPTION)
                for output in cesubloc.outputs:
                    output['valide'] = False
            cesubloc.c_exesubloc_overwriting_outputs()
        #print ("<PREVIOUS> retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    return cesubloc.outputs[pio]['var'], cesubloc.outputs[pio]['valide']
def c_exesubloc_select (pebloc, pieb, pio, pthread):
    """ exécution du bloc SELECTION (dans la boucler écurcive)"""
    #les index IOs
    #I_GATE=0
    #I_IF0=1
    #I_IF1=2
    #O_OUT
    cesubloc = pebloc.sublocs[pieb]
    #print ("<SELECT> les paramètres sont: pieb=", pieb, ",   pio=", pio, ",   counter=", pthread['counter'])
    if cesubloc.header['counter'] == pthread['counter']:
        pass
        #print ("cesubloc['counter'] == pthread['counter']: =", pthread['counter'], "   (output[", pio, "] inchangée)")
    else:
        cesubloc.header['counter'] = pthread['counter']
        try:
            pebloc.c_exebloc_recup_input (pieb, pthread, 0)
            if cesubloc.inputs[0]['var']: index = 2
            else:                         index = 1
            pebloc.c_exebloc_recup_input (pieb, pthread, index)
            cesubloc.outputs[0]['valide'] = cesubloc.inputs[0]['valide'] and cesubloc.inputs[index]['valide']
            cesubloc.outputs[0]['var']    = cesubloc.inputs[index]['var']
        except:
            #print ("<SELECT>", PARAM_TEXT_EXCEPTION)
            for output in cesubloc.outputs:
                output['valide'] = False
        cesubloc.c_exesubloc_overwriting_outputs()
    #print ("<SELECT> retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    return cesubloc.outputs[pio]['var'], cesubloc.outputs[pio]['valide']
def c_exesubloc_validRead (pebloc, pieb, pio, pthread):
    """ exécution du bloc VALIDREAD: lecture de la validité"""
    cesubloc = pebloc.sublocs[pieb]
    #print ("<VALIDREAD> les paramètres sont: pieb=", pieb, ",   pio=", pio, ",   counter=", pthread['counter'])
    if cesubloc.header['counter'] == pthread['counter']:
        pass
        #print ("<VALIDREAD>", "cesubloc['counter'] == pthread['counter']: =", pthread['counter'], "   (output[", pio, "] inchangée)")
    else:
        cesubloc.header['counter'] = pthread['counter']
        try:
            pebloc.c_exebloc_recup_input (pieb, pthread, 0)
            cesubloc.c_exesubloc_validation_standard()
            cesubloc.outputs[0]['var'] = cesubloc.inputs[0]['valide']
            cesubloc.outputs[0]['valide'] = True
        except:
            #print ("<VALIDREAD>", PARAM_TEXT_EXCEPTION)
            for output in cesubloc.outputs:
                output['valide'] = False
        cesubloc.c_exesubloc_overwriting_outputs()
    #print ("<VALIREAD> retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    return cesubloc.outputs[pio]['var'], cesubloc.outputs[pio]['valide']
def c_exesubloc_validWrite (pebloc, pieb, pio, pthread):
    """ exécution du bloc VALIDWRITE: surcharge la validité"""
    cesubloc = pebloc.sublocs[pieb]

    #print ("<VALIWRITE> les paramètres sont: pieb=", pieb, ",   pio=", pio, ",   counter=", pthread['counter'])
    if cesubloc.header['counter'] == pthread['counter']:
        pass
        #print ("<VALIDWRITE>", "  cesubloc['counter'] == pthread['counter']: =", pthread['counter'], "   (output[", pio, "] inchangée)")
    else:
        cesubloc.header['counter'] = pthread['counter']
        try:
            pebloc.c_exebloc_recup_inputs(pieb, pthread)
            cesubloc.c_exesubloc_validation_standard()
            cesubloc.outputs[0]['var'] = cesubloc.inputs[0]['var']
            cesubloc.outputs[0]['valide'] = cesubloc.inputs[1]['var']
        except:
            #print ("<VALIDWRITE>", PARAM_TEXT_EXCEPTION)
            for output in cesubloc.outputs:
                output['valide'] = False
        cesubloc.c_exesubloc_overwriting_outputs()
    #print ("<VALIDWRITE> retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    return cesubloc.outputs[pio]['var'], cesubloc.outputs[pio]['valide']
def c_exesubloc_time (pebloc, pieb, pio, pthread):
    """ exécution du bloc TIME retourne le temps de cycle (dans la boucler écurcive)"""
    cesubloc = pebloc.sublocs[pieb]
    #print ("<TIME> les paramètres reçus sont: pieb=", pieb, ",   pio=", pio, ",   counter=", pthread['counter'])
    if cesubloc.header['counter'] == pthread['counter']:
        pass
        #print ("<TIME>", "  cesubloc['counter'] == pthread['counter']: =", pthread['counter'], "   (output[", pio, "] inchangée)")
    else:
        cesubloc.header['counter'] = pthread['counter']
        try:
            cesubloc.outputs[0]['var'] = time.time()
            cesubloc.outputs[0]['valide'] = True
        except:
            #print ("<TIME>", PARAM_TEXT_EXCEPTION)
            for output in cesubloc.outputs:
                output['valide'] = False
        cesubloc.c_exesubloc_overwriting_outputs()
    #print ("<TIME> retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    return cesubloc.outputs[pio]['var'], cesubloc.outputs[pio]['valide']
def c_exesubloc_dt (pebloc, pieb, pio, pthread):
    """ exécution du bloc DT retourne le temps de cycle téhorique et mesurée de la tâche qui exécute ce bloc (dans la boucler écurcive)"""
    cesubloc = pebloc.sublocs[pieb]
    #print ("<DT> les paramètres reçus sont: pieb=", pieb, ",   pio=", pio, ",   counter=", pthread['counter'])
    if cesubloc.header['counter'] == pthread['counter']:
        pass
        #print ("<DT>", "  cesubloc['counter'] == pthread['counter']: =", pthread['counter'], "   (output[", pio, "] inchangée)")
    else:
        cesubloc.header['counter'] = pthread['counter']
        try:
            cesubloc.outputs[0]['valide'] = True
            cesubloc.outputs[1]['valide'] = True
            cesubloc.outputs[0]['var'] = pthread['period']
            cesubloc.outputs[1]['var'] = pthread['cycle_time']
        except:
            #print ("<DT>", PARAM_TEXT_EXCEPTION)
            for output in cesubloc.outputs:
                output['valide'] = False
        cesubloc.c_exesubloc_overwriting_outputs()
    #print ("<DT> retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    return cesubloc.outputs[pio]['var'], cesubloc.outputs[pio]['valide']
def c_exesubloc_comp (pebloc, pieb, pio, pthread):
    """ exécution du bloc COMPARE (dans la boucler écurcive)"""
    cesubloc = pebloc.sublocs[pieb]
    #print ("<COMP> les paramètres sont: pieb=", pieb, ",   pio=", pio, ",   counter=", pthread['counter'])
    if cesubloc.header['counter'] == pthread['counter']:
        pass
        #print ("<COMP>", "  cesubloc['counter'] == pthread['counter']: =", pthread['counter'], "   (output[", pio, "] inchangée)")
    else:
        cesubloc.header['counter'] = pthread['counter']
        try:
            pebloc.c_exebloc_recup_inputs(pieb, pthread)
            cesubloc.c_exesubloc_validation_standard()
            cesubloc.outputs[0]['var'] = cesubloc.inputs[0]['var'] >  cesubloc.inputs[1]['var']
            cesubloc.outputs[1]['var'] = cesubloc.inputs[0]['var'] == cesubloc.inputs[1]['var']
            cesubloc.outputs[2]['var'] = cesubloc.inputs[0]['var'] <  cesubloc.inputs[1]['var']
            cesubloc.c_exesubloc_overwriting_outputs()
        except:
            #print ("<COMP>", PARAM_TEXT_EXCEPTION)
            for output in cesubloc.outputs:
                output['valide'] = False
    #print ("<COMP> retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    return cesubloc.outputs[pio]['var'], cesubloc.outputs[pio]['valide']
def c_exesubloc_and (pebloc, pieb, pio, pthread):
    """ exécution du bloc a et b (dans la boucle récurcive)"""
    cesubloc = pebloc.sublocs[pieb]
    #print ("<AND> les paramètres sont: pieb=", pieb, ",   pio=", pio, ",   counter=", pthread['counter'])
    if cesubloc.header['counter'] == pthread['counter']:
        pass
        #print ("<AND>", "  cesubloc['counter'] == pthread['counter']: =", pthread['counter'], "   (output[", pio, "] inchangée)")
    else:
        cesubloc.header['counter'] = pthread['counter']
        try:
            pebloc.c_exebloc_recup_inputs(pieb, pthread)
            cesubloc.c_exesubloc_validation_standard()
            cesubloc.outputs[0]['var'] = cesubloc.inputs[0]['var'] and cesubloc.inputs[1]['var']
        except:
            #print ("<AND>", PARAM_TEXT_EXCEPTION)
            for output in cesubloc.outputs:
                output['valide'] = False
        cesubloc.c_exesubloc_overwriting_outputs()
    #print ("<AND> retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    return cesubloc.outputs[pio]['var'], cesubloc.outputs[pio]['valide']
def c_exesubloc_or (pebloc, pieb, pio, pthread):
    """ exécution du bloc a ou b (dans la boucle récurcive)"""
    cesubloc = pebloc.sublocs[pieb]
    #print ("<OR> les paramètres sont: pieb=", pieb, ",   pio=", pio, ",   counter=", pthread['counter'])
    if cesubloc.header['counter'] == pthread['counter']:
        pass
        #print ("<OR>", "  cesubloc['counter'] == pthread['counter']: =", pthread['counter'], "   (output[", pio, "] inchangée)")
    else:
        cesubloc.header['counter'] = pthread['counter']
        try:
            pebloc.c_exebloc_recup_inputs(pieb, pthread)
            cesubloc.c_exesubloc_validation_standard()
            cesubloc.outputs[0]['var'] = cesubloc.inputs[0]['var'] or cesubloc.inputs[1]['var']
        except:
            #print ("<OR>", PARAM_TEXT_EXCEPTION)
            for output in cesubloc.outputs:
                output['valide'] = False
        cesubloc.c_exesubloc_overwriting_outputs()
    #print ("<OR> retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    return cesubloc.outputs[pio]['var'], cesubloc.outputs[pio]['valide']
def c_exesubloc_not (pebloc, pieb, pio, pthread):
    """ exécution du bloc a = non(b) (dans la boucler écurcive)"""
    cesubloc = pebloc.sublocs[pieb]
    #print ("<NOT> les paramètres sont: pieb=", pieb, ",   pio=", pio, ",   counter=", pthread['counter'])
    if cesubloc.header['counter'] == pthread['counter']:
        pass
        #print ("<NOT>", "  cesubloc['counter'] == pthread['counter']: =", pthread['counter'], "   (output[", pio, "] inchangée)")
    else:
        cesubloc.header['counter'] = pthread['counter']
        try:
            pebloc.c_exebloc_recup_input(pieb, pthread, 0)
            cesubloc.c_exesubloc_validation_standard()
            cesubloc.outputs[0]['var'] = not cesubloc.inputs[0]['var']
        except:
            #print ("<NOT>", PARAM_TEXT_EXCEPTION)
            for output in cesubloc.outputs:
                output['valide'] = False
        cesubloc.c_exesubloc_overwriting_outputs()
    #print ("<NOT> retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    return cesubloc.outputs[pio]['var'], cesubloc.outputs[pio]['valide']
def c_exesubloc_edge (pebloc, pieb, pio, pthread):
    """ exécution du bloc détection de fronts (dans la boucle récurcive)"""
    # les index des IOs
    #I_IN = 0
    #I_RISE = 1
    #I_FALL = 2
    #O_OUT = 0
    #O_IN_NM1 = 1
    cesubloc = pebloc.sublocs[pieb]
    #print ("<EDGE> les paramètres sont: pieb=", pieb, ",   pio=", pio, ",   counter=", pthread['counter'])
    if cesubloc.header['counter'] == pthread['counter']:
        pass
        #print ("<EDGE>", "  cesubloc['counter'] == pthread['counter']: =", pthread['counter'], "   (output[", pio, "] inchangée)")
    else:
        cesubloc.header['counter'] = pthread['counter']
        try:
            pebloc.c_exebloc_recup_inputs(pieb, pthread)
            cesubloc.outputs[0]['var'] = (cesubloc.inputs[1]['var'] and      cesubloc.inputs[0]['var']  and not cesubloc.outputs[1]['var'])\
                                      or (cesubloc.inputs[2]['var'] and (not cesubloc.inputs[0]['var']) and     cesubloc.outputs[1]['var'])
            cesubloc.outputs[0]['valide'] = cesubloc.outputs[1]['valide'] and cesubloc.inputs[0]['valide'] and cesubloc.inputs[1]['valide'] and cesubloc.inputs[2]['valide']
            cesubloc.outputs[1]['var'] = cesubloc.inputs[0]['var']
            cesubloc.outputs[1]['valide'] = cesubloc.inputs[0]['valide']
            cesubloc.c_exesubloc_overwriting_outputs()
        except:
            #print ("<EDGE>", PARAM_TEXT_EXCEPTION)
            for output in cesubloc.outputs:
                output['valide'] = False
        cesubloc.c_exesubloc_overwriting_outputs()
    #print ("<EDGE> retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    return cesubloc.outputs[pio]['var'], cesubloc.outputs[pio]['valide']
def c_exesubloc_cablin (pebloc, pieb, pio, pthread):
    """ exécution du bloc CABLIN (dans la boucle récurcive)"""
    cesubloc = pebloc.sublocs[pieb]
    #print ("<CABLIN> les paramètres sont: pieb=", pieb, ",   pio=", pio, ",   counter=", pthread['counter'])
    if cesubloc.header['counter'] == pthread['counter']:
        pass
        #print ("<CABLIN>", "  cesubloc['counter'] == pthread['counter']: =", pthread['counter'], "   (output[", pio, "] inchangée)")
    else:
        cesubloc.header['counter'] = pthread['counter']
        try:
            pebloc.c_exebloc_recup_inputs(pieb, pthread)
            cesubloc.outputs[0]['valide'] = (cesubloc.inputs[0]['valide'], cesubloc.inputs[1]['valide'])
            cesubloc.outputs[0]['var']    = (cesubloc.inputs[0]['var'], cesubloc.inputs[1]['var'])
        except:
            #print ("<CABLIN>", PARAM_TEXT_EXCEPTION)
            for output in cesubloc.outputs:
                output['valide'] = False
        cesubloc.c_exesubloc_overwriting_outputs()
    #print ("<CABLIN> retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    if 'forced' in cesubloc.outputs[pio]:
        cesubloc.outputs[pio]['var'] = cesubloc.outputs[pio]['forced_value']
        cesubloc.outputs[pio]['valide'] = cesubloc.outputs[pio]['forced_valide']
    return cesubloc.outputs[pio]['var'], cesubloc.outputs[pio]['valide']
def c_exesubloc_cablout (pebloc, pieb, pio, pthread):
    """ exécution du bloc CABLOUT (dans la boucler écurcive)"""
    cesubloc = pebloc.sublocs[pieb]
    #print ("<CABLOUT> les paramètres sont: pieb=", pieb, ",   pio=", pio, ",   counter=", pthread['counter'])
    if cesubloc.header['counter'] == pthread['counter']:
        pass
        #print ("<CABLOUT>", "  cesubloc['counter'] == pthread['counter']: =", pthread['counter'], "   (output[", pio, "] inchangée)")
    else:
        cesubloc.header['counter'] = pthread['counter']
        try:
            pebloc.c_exebloc_recup_inputs(pieb, pthread)
            #print (f"c_exesubloc_cablout: cesubloc.inputs[0]={cesubloc.inputs[0]}")
            cesubloc.outputs[0]['var'] = cesubloc.inputs[0]['var'][0]
            cesubloc.outputs[1]['var'] = cesubloc.inputs[0]['var'][1]
            cesubloc.outputs[0]['valide'] = cesubloc.inputs[0]['valide'][0]
            cesubloc.outputs[1]['valide'] = cesubloc.inputs[0]['valide'][1]
        except:
            #print ("<CABLOUT>", PARAM_TEXT_EXCEPTION)
            for output in cesubloc.outputs:
                output['valide'] = False
        cesubloc.c_exesubloc_overwriting_outputs()
    #print ("<CABLOUT> retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    return cesubloc.outputs[pio]['var'], cesubloc.outputs[pio]['valide']
def c_exesubloc_add (pebloc, pieb, pio, pthread):
    """ exécution du bloc ADDITION (dans la boucler écurcive)"""
    cesubloc = pebloc.sublocs[pieb]
    #print ("<ADD> les paramètres reçus sont: pieb=", pieb, ",   pio=", pio, ",   counter=", pthread['counter'])
    if cesubloc.header['counter'] == pthread['counter']:
        pass
        #print ("<ADD>", "  cesubloc['counter'] == pthread['counter']: =", pthread['counter'], "   (output[", pio, "] inchangée)")
    else:
        cesubloc.header['counter'] = pthread['counter']
        try:
            pebloc.c_exebloc_recup_inputs(pieb, pthread)
            cesubloc.c_exesubloc_validation_standard()
            cesubloc.outputs[0]['var'] = cesubloc.inputs[0]['var'] + cesubloc.inputs[1]['var']
        except:
            #print ("<ADD>", PARAM_TEXT_EXCEPTION)
            for output in cesubloc.outputs:
                output['valide'] = False
        cesubloc.c_exesubloc_overwriting_outputs()
    #print ("<ADD> retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    return cesubloc.outputs[pio]['var'], cesubloc.outputs[pio]['valide']
def c_exesubloc_sub (pebloc, pieb, pio, pthread):
    """ exécution du bloc SOUSTRACTION (dans la boucler écurcive)"""
    cesubloc = pebloc.sublocs[pieb]
    #print ("<SUB> les paramètres sont: pieb=", pieb, ",   pio=", pio, ",   counter=", pthread['counter'])
    if cesubloc.header['counter'] == pthread['counter']:
        pass
        #print ("<SUB>", "  cesubloc['counter'] == pthread['counter']: =", pthread['counter'], "   (output[", pio, "] inchangée)")
    else:
        cesubloc.header['counter'] = pthread['counter']
        try:
            pebloc.c_exebloc_recup_inputs(pieb, pthread)
            cesubloc.c_exesubloc_validation_standard()
            cesubloc.outputs[0]['var'] = cesubloc.inputs[0]['var'] - cesubloc.inputs[1]['var']
        except:
            #print ("<SUB>", PARAM_TEXT_EXCEPTION)
            for output in cesubloc.outputs:
                output['valide'] = False
        cesubloc.c_exesubloc_overwriting_outputs()
    #print ("<SUB> retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    return cesubloc.outputs[pio]['var'], cesubloc.outputs[pio]['valide']
def c_exesubloc_mult (pebloc, pieb, pio, pthread):
    """ exécution du bloc MULTIPLICATION (dans la boucler écurcive)"""
    cesubloc = pebloc.sublocs[pieb]
    #print ("<MULT> les paramètres sont: pieb=", pieb, ",   pio=", pio, ",   counter=", pthread['counter'])
    if cesubloc.header['counter'] == pthread['counter']:
        pass
        #print ("<MULT>", "  cesubloc['counter'] == pthread['counter']: =", pthread['counter'], "   (output[", pio, "] inchangée)")
    else:
        cesubloc.header['counter'] = pthread['counter']
        try:
            pebloc.c_exebloc_recup_inputs(pieb, pthread)
            cesubloc.c_exesubloc_validation_standard()
            cesubloc.outputs[0]['var'] = cesubloc.inputs[0]['var'] * cesubloc.inputs[1]['var']
        except:
            #print ("<MULT>", PARAM_TEXT_EXCEPTION)
            for output in cesubloc.outputs:
                output['valide'] = False
        cesubloc.c_exesubloc_overwriting_outputs()
    #print ("<MUL> retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    return cesubloc.outputs[pio]['var'], cesubloc.outputs[pio]['valide']
def c_exesubloc_div (pebloc, pieb, pio, pthread):
    """ exécution du bloc DIVISION (dans la boucler écurcive)"""
    cesubloc = pebloc.sublocs[pieb]
    #print ("<DIV> les paramètres sont: pieb=", pieb, ",   pio=", pio, ",   counter=", pthread['counter'])
    if cesubloc.header['counter'] == pthread['counter']:
        pass
        #print ("<DIV>", "  cesubloc['counter'] == pthread['counter']: =", pthread['counter'], "   (output[", pio, "] inchangée)")
    else:
        cesubloc.header['counter'] = pthread['counter']
        try:
            pebloc.c_exebloc_recup_inputs(pieb, pthread)
            cesubloc.c_exesubloc_validation_standard()
            cesubloc.outputs[0]['var'] = cesubloc.inputs[0]['var'] / cesubloc.inputs[1]['var']
        except:
            #print ("<DIV>", PARAM_TEXT_EXCEPTION)
            for output in cesubloc.outputs:
                output['valide'] = False
        cesubloc.c_exesubloc_overwriting_outputs()
    #print ("<DIV> retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    return cesubloc.outputs[pio]['var'], cesubloc.outputs[pio]['valide']
def c_exesubloc_minmax (pebloc, pieb, pio, pthread):
    """ exécution du bloc MINMAX (dans la boucler écurcive)"""
    cesubloc = pebloc.sublocs[pieb]
    #print ("<MINMAX> les paramètres sont: pieb=", pieb, ",   pio=", pio, ",   counter=", pthread['counter'])
    if cesubloc.header['counter'] == pthread['counter']:
        pass
        #print ("<MINMAX>", "  cesubloc['counter'] == pthread['counter']: =", pthread['counter'], "   (output[", pio, "] inchangée)")
    else:
        cesubloc.header['counter'] = pthread['counter']
        try:
            pebloc.c_exebloc_recup_inputs(pieb, pthread)
            cesubloc.c_exesubloc_validation_standard()
            cesubloc.outputs[0]['var'] = max(cesubloc.inputs[0]['var'], cesubloc.inputs[1]['var'])
            cesubloc.outputs[1]['var'] = min(cesubloc.inputs[0]['var'], cesubloc.inputs[1]['var'])
        except:
            #print ("<MINMAX>", PARAM_TEXT_EXCEPTION)
            for output in cesubloc.outputs:
                output['valide'] = False
        cesubloc.c_exesubloc_overwriting_outputs()
    #print ("<MINMAX> retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    return cesubloc.outputs[pio]['var'], cesubloc.outputs[pio]['valide']
def c_exesubloc_const_pi (pebloc, pieb, pio, pthread):
    """ exécution du bloc CONST_PI (dans la boucler écurcive)"""
    cesubloc = pebloc.sublocs[pieb]
    #print ("<CONST_PI> les paramètres sont: pieb=", pieb, ",   pio=", pio, ",   counter=", pthread['counter'])
    if cesubloc.header['counter'] == pthread['counter']:
        pass
        #print ("<CONST_PI>", "  cesubloc['counter'] == pthread['counter']: =", pthread['counter'], "   (output[", pio, "] inchangée)")
    else:
        cesubloc.header['counter'] = pthread['counter']
        try:
            cesubloc.outputs[0]['var'] =  math.pi
            cesubloc.outputs[0]['valide'] =  True
        except:
            #print ("<CONST_PI>", PARAM_TEXT_EXCEPTION)
            for output in cesubloc.outputs:
                output['valide'] = False
        cesubloc.c_exesubloc_overwriting_outputs()
    #print ("<CONST_PI> retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    return cesubloc.outputs[pio]['var'], cesubloc.outputs[pio]['valide']
def c_exesubloc_memory (pebloc, pieb, pio, pthread):
    """ exécution du bloc bascule RS (dans la boucle récurcive)"""
    # les index des IOs
    #I_SET = 0
    #I_RESET = 1
    #I_RESET_PRIORITAIRE = 2
    #O_OUT = 0
    cesubloc = pebloc.sublocs[pieb]
    #print ("<MEMORY> les paramètres sont: pieb=", pieb, ",   pio=", pio, ",   counter=", pthread['counter'])
    if cesubloc.header['counter'] == pthread['counter']:
        pass
        #print ("<MEMORY>", "  cesubloc['counter'] == pthread['counter']: =", pthread['counter'], "   (output[", pio, "] inchangée)")
    else:
        cesubloc.header['counter'] = pthread['counter']
        try:
            pebloc.c_exebloc_recup_inputs(pieb, pthread)
            cesubloc.c_exesubloc_validation_standard()
            if cesubloc.inputs[0]['var'] and (not cesubloc.inputs[2]['var'] or not cesubloc.inputs[1]['var']):
                cesubloc.outputs[0]['var'] = True
            if cesubloc.inputs[1]['var'] and (cesubloc.inputs[2]['var']  or not cesubloc.inputs[0]['var']):
                cesubloc.outputs[0]['var'] = False
        except:
            #print ("<MEMORY>", PARAM_TEXT_EXCEPTION)
            for output in cesubloc.outputs:
                output['valide'] = False
        cesubloc.c_exesubloc_overwriting_outputs()
    #print ("<MEMORY> retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    return cesubloc.outputs[pio]['var'], cesubloc.outputs[pio]['valide']
def c_exesubloc_delay (pebloc, pieb, pio, pthread):
    """ exécution du bloc retard à la montée et à la descente (dans la boucle récurcive)"""
    # les index des IO
    I_IN = 0
    I_RISE = 1
    I_DELAY = 2
    O_OUT = 0
    O_RT = 1 #remening time
    O_IN_NM1 = 2
    cesubloc = pebloc.sublocs[pieb]
    #print ("<DELAY> les paramètres sont: pieb=", pieb, ",   pio=", pio, ",   counter=", pthread['counter'])
    if cesubloc.header['counter'] == pthread['counter']:
        pass
        #print ("<DELAY>", "  cesubloc['counter'] == pthread['counter']: =", pthread['counter'], "   (output[", pio, "] inchangée)")
    else:
        cesubloc.header['counter'] = pthread['counter']
        try:
            pebloc.c_exebloc_recup_inputs(pieb, pthread)
            if cesubloc.inputs[I_RISE]['var']:
                if cesubloc.inputs[I_DELAY]['var'] > 0:
                    if  cesubloc.inputs[I_IN]['var'] and not cesubloc.outputs[O_IN_NM1]['var']:
                        cesubloc.outputs[O_RT]['var'] = cesubloc.inputs[I_DELAY]['var']
                    if  not cesubloc.inputs[I_IN]['var']:
                        cesubloc.outputs[O_RT]['var'] = 0                    
                    if cesubloc.outputs[O_RT]['var'] > 0:
                        cesubloc.outputs[O_RT]['var'] -= pthread['cycle_time']
                        rise_delay_active = True
                    else:
                        rise_delay_active = False
                else:
                    rise_delay_active = False
                fall_delay_active = False
            else:
                if cesubloc.inputs[I_DELAY]['var'] > 0:
                    if (not cesubloc.inputs[I_IN]['var']) and cesubloc.outputs[O_IN_NM1]['var']:
                        cesubloc.outputs[O_RT]['var'] = cesubloc.inputs[I_DELAY]['var']
                    if  cesubloc.inputs[I_IN]['var']:
                        cesubloc.outputs[O_RT]['var'] = 0                    
                    if cesubloc.outputs[O_RT]['var'] > 0:
                        cesubloc.outputs[O_RT]['var'] -= pthread['cycle_time']
                        fall_delay_active = True
                    else:
                        fall_delay_active = False
                else:
                    fall_delay_active = False
                rise_delay_active = False
            cesubloc.outputs[O_OUT]['var'] = cesubloc.inputs[I_IN]['var'] and (not rise_delay_active) or fall_delay_active
            cesubloc.outputs[O_OUT]['valide'] = cesubloc.outputs[O_IN_NM1]['valide'] and cesubloc.inputs[I_IN]['valide'] and cesubloc.inputs[I_RISE]['valide'] and cesubloc.inputs[I_DELAY]['valide']
            cesubloc.outputs[O_IN_NM1]['var'] = cesubloc.inputs[I_IN]['var']
            cesubloc.outputs[O_IN_NM1]['valide'] = cesubloc.inputs[I_IN]['valide']
        except:
            #print ("<DELAY>", PARAM_TEXT_EXCEPTION)
            for output in cesubloc.outputs:
                output['valide'] = False
        cesubloc.c_exesubloc_overwriting_outputs()
    #print ("<DELAY> retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    return cesubloc.outputs[pio]['var'], cesubloc.outputs[pio]['valide']
def c_exesubloc_clock (pebloc, pieb, pio, pthread):
    """ exécution du bloc CLOCK retourne un bool qui reste VRAI n seconde, puis reste FAUX m secondes, puise ainsi de suite (dans la boucler écurcive)"""
    # les index des IOs
    I_T_ON = 0
    I_T_OFF = 1
    O_CLOCK = 0
    O_RT = 1
    cesubloc = pebloc.sublocs[pieb]
    #print ("<CLOCK> les paramètres reçus sont: pieb=", pieb, ",   pio=", pio, ",   counter=", pthread['counter'])
    if cesubloc.header['counter'] == pthread['counter']:
        pass
        #print ("<CLOCK>", "  cesubloc['counter'] == pthread['counter']: =", pthread['counter'], "   (output[", pio, "] inchangée)")
    else:
        cesubloc.header['counter'] = pthread['counter']
        try:
            pebloc.c_exebloc_recup_inputs(pieb, pthread)
            cesubloc.c_exesubloc_validation_standard()
            if 'forced' in cesubloc.outputs[O_RT]:
                cesubloc.outputs[O_RT]['var']    = cesubloc.outputs[O_RT]['forced_value'] 
                cesubloc.outputs[O_RT]['valide'] = cesubloc.outputs[O_RT]['forced_valide']
            else:
                if cesubloc.outputs[O_RT]['var'] > 0:
                    cesubloc.outputs[O_RT]['var'] -= pthread['cycle_time']
                else:
                    if cesubloc.outputs[O_CLOCK]['var']:
                        cesubloc.outputs[O_CLOCK]['var'] = False
                        cesubloc.outputs[O_RT]['var'] = cesubloc.inputs[I_T_OFF]['var']
                    else:
                        cesubloc.outputs[O_CLOCK]['var'] = True
                        cesubloc.outputs[O_RT]['var'] = cesubloc.inputs[I_T_ON]['var']
        except:
            #print ("<CLOCK>", PARAM_TEXT_EXCEPTION)
            for output in cesubloc.outputs:
                output['valide'] = False
        cesubloc.c_exesubloc_overwriting_outputs()
    #print ("<CLOCK> retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    return cesubloc.outputs[pio]['var'], cesubloc.outputs[pio]['valide']
def c_exesubloc_limit (pebloc, pieb, pio, pthread):
    """ exécution du bloc LIMIT (dans la boucler écurcive)"""
    cesubloc = pebloc.sublocs[pieb]
    #print ("<LIMIT> les paramètres sont: pieb=", pieb, ",   pio=", pio, ",   counter=", pthread['counter'])
    if cesubloc.header['counter'] == pthread['counter']:
        pass
        #print ("<LIMIT>", "  cesubloc['counter'] == pthread['counter']: =", pthread['counter'], "   (output[", pio, "] inchangée)")
    else:
        cesubloc.header['counter'] = pthread['counter']
        try:
            pebloc.c_exebloc_recup_inputs(pieb, pthread)
            cesubloc.c_exesubloc_validation_standard()
            if cesubloc.inputs[0]['var'] < cesubloc.inputs[2]['var']:
                cesubloc.outputs[0]['valide'] = False
                cesubloc.outputs[1]['valide'] = False
                cesubloc.outputs[2]['valide'] = False
                cesubloc.outputs[1]['var'] = cesubloc.inputs[1]['var']
            elif cesubloc.inputs[1]['var'] > cesubloc.inputs[0]['var']:
                cesubloc.outputs[0]['var'] = True
                cesubloc.outputs[1]['var'] = cesubloc.inputs[0]['var']
                cesubloc.outputs[2]['var'] = False
            elif cesubloc.inputs[1]['var'] < cesubloc.inputs[2]['var']:
                cesubloc.outputs[0]['var'] = False
                cesubloc.outputs[1]['var'] = cesubloc.inputs[2]['var']
                cesubloc.outputs[2]['var'] = True
            else:
                cesubloc.outputs[0]['var'] = False
                cesubloc.outputs[1]['var'] = cesubloc.inputs[1]['var']
                cesubloc.outputs[2]['var'] = False
        except:
            #print ("<LIMIT>", PARAM_TEXT_EXCEPTION)
            for output in cesubloc.outputs:
                output['valide'] = False
        cesubloc.c_exesubloc_overwriting_outputs()
    #print ("<LIMIT>", " LIMIT retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    return cesubloc.outputs[pio]['var'], cesubloc.outputs[pio]['valide']
def c_exesubloc_differencial (pebloc, pieb, pio, pthread):
    """ exécution du bloc DIFFERENCIAL: lecture de la validité"""
    cesubloc = pebloc.sublocs[pieb]
    #print ("<DIFFERENCIAL> les paramètres sont: pieb=", pieb, ",   pio=", pio, ",   counter=", pthread['counter'])
    if cesubloc.header['counter'] == pthread['counter']:
        pass
        #print ("<DIFFERENCIAL>", "cesubloc['counter'] == pthread['counter']: =", pthread['counter'], "   (output[", pio, "] inchangée)")
    else:
        cesubloc.header['counter'] = pthread['counter']
        try:
            pebloc.c_exebloc_recup_input (pieb, pthread, 0)
            cesubloc.outputs[0]['var'] = (cesubloc.inputs[0]['var'] - cesubloc.outputs[1]['var']) / pthread['cycle_time']
            cesubloc.outputs[0]['valide'] = cesubloc.inputs[0]['valide'] and cesubloc.outputs[1]['valide'] 
            cesubloc.outputs[1]['var'] = cesubloc.inputs[0]['var']
            cesubloc.outputs[1]['valide'] = cesubloc.inputs[0]['valide']
        except:
            #print ("<DIFF>", PARAM_TEXT_EXCEPTION)
            for output in cesubloc.outputs:
                output['valide'] = False
        cesubloc.c_exesubloc_overwriting_outputs()
    #print ("<DIFFERENCIAL> retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    return cesubloc.outputs[pio]['var'], cesubloc.outputs[pio]['valide']
def c_exesubloc_integrator (pebloc, pieb, pio, pthread):
    """ exécution du bloc DIFF: lecture de la validité"""
    # les index des IOs
    I_H=0 # limite haute
    I_IN = 1
    I_L=2 # limite basse
    I_TAU = 3 # constante de temps d'intégration
    I_SET = 4
    I_PRESET =5
    O_H = 0 # indicateur saturation haute
    O_OUT = 1
    O_L = 2 # indicateur saturation basse
    cesubloc = pebloc.sublocs[pieb]
    #print ("<INTEGRATOR> les paramètres sont: pieb=", pieb, ",   pio=", pio, ",   counter=", pthread['counter'])
    if cesubloc.header['counter'] == pthread['counter']:
        pass
        #print ("<INTEGRATOR>", "cesubloc['counter'] == pthread['counter']: =", pthread['counter'], "   (output[", pio, "] inchangée)")
    else:
        cesubloc.header['counter'] = pthread['counter']
        try:
            pebloc.c_exebloc_recup_inputs(pieb, pthread)
            cesubloc.c_exesubloc_validation_standard()
            delta = (cesubloc.inputs[I_IN]['var'] * pthread['cycle_time']) / cesubloc.inputs[I_TAU]['var']
            if cesubloc.inputs[I_SET]['var']:
                integrator = cesubloc.inputs[I_PRESET]['var']
            else:
                integrator = delta + cesubloc.outputs[O_OUT]['var']

            if not cesubloc.inputs[I_SET]['var'] and not cesubloc.outputs[O_OUT]['valide']:
                cesubloc.outputs[O_H]['valide'] = False
                cesubloc.outputs[O_OUT]['valide'] = False
                cesubloc.outputs[O_L]['valide'] = False

            if cesubloc.inputs[I_H]['var'] < cesubloc.inputs[I_L]['var']:
                cesubloc.outputs[O_H]['valide'] = False
                cesubloc.outputs[O_OUT]['valide'] = False
                cesubloc.outputs[O_L]['valide'] = False
                cesubloc.outputs[O_OUT]['var'] = integrator
            elif integrator > cesubloc.inputs[I_H]['var']:
                cesubloc.outputs[O_H]['var'] = True
                cesubloc.outputs[O_OUT]['var'] = cesubloc.inputs[I_H]['var']
                cesubloc.outputs[O_L]['var'] = False
            elif integrator < cesubloc.inputs[I_L]['var']:
                cesubloc.outputs[O_H]['var'] = False
                cesubloc.outputs[O_OUT]['var'] = cesubloc.inputs[I_L]['var']
                cesubloc.outputs[O_L]['var'] = True
            else:
                cesubloc.outputs[O_H]['var'] = False
                cesubloc.outputs[O_OUT]['var'] = integrator
                cesubloc.outputs[O_L]['var'] = False
        except:
            #print ("<INTEGRATOR>", PARAM_TEXT_EXCEPTION)
            for output in cesubloc.outputs:
                output['valide'] = False
        cesubloc.c_exesubloc_overwriting_outputs()
    #print ("<INTEGRATOR> retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    return cesubloc.outputs[pio]['var'], cesubloc.outputs[pio]['valide']
def c_exesubloc_filter_FO (pebloc, pieb, pio, pthread):
    """ exécution du bloc filtre du 1er ordre (dans la boucle récurcive)"""
    # les index des IO
    #I_IN = 0
    #I_TAU = 1 # time constant
    #O_out = 0
    #O_in_nm1 = 0 # previous input
    cesubloc = pebloc.sublocs[pieb]
    #print ("<PULSE> les paramètres sont: pieb=", pieb, ",   pio=", pio, ",   counter=", pthread['counter'])
    if cesubloc.header['counter'] == pthread['counter']:
        pass
        #print ("<FILTER_FO>", "  cesubloc['counter'] == pthread['counter']: =", pthread['counter'], "   (output[", pio, "] inchangée)")
    else:
        cesubloc.header['counter'] = pthread['counter']
        try:
            pebloc.c_exebloc_recup_inputs(pieb, pthread)
            #gain = pthread['period']    / cesubloc.inputs[1]['var']
            gain = pthread['cycle_time'] / cesubloc.inputs[1]['var']
            if cesubloc.outputs[0]['valide'] and (pthread['cycle_time'] < cesubloc.inputs[1]['var']):
                cesubloc.outputs[0]['var'] += gain * cesubloc.inputs[0]['var'] - gain * cesubloc.outputs[0]['var']
            else:
                cesubloc.outputs[0]['var'] = cesubloc.inputs[0]['var']
            cesubloc.outputs[0]['valide'] = cesubloc.inputs[0]['valide'] and cesubloc.inputs[1]['valide']
        except:
            #print ("<FILTER_FO>", PARAM_TEXT_EXCEPTION)
            for output in cesubloc.outputs:
                output['valide'] = False
        cesubloc.c_exesubloc_overwriting_outputs()
    #print ("<FILTER_FO> retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    return cesubloc.outputs[pio]['var'], cesubloc.outputs[pio]['valide']
def c_exesubloc_input_output (pebloc, pieb, pio, pthread):
    """ exécution du bloc de récupération d'output d'un autre bloc exécutable (dans la boucle récurcive)"""
    # les index des IO
    #I_BLOC_NAME = 0
    #I_OUTPUT_ID = 1 # time constant
    #O_out = 0
    cesubloc = pebloc.sublocs[pieb]
    #print ("<INPUT_OUTPUT> les paramètres sont: pieb=", pieb, ",   pio=", pio, ",   counter=", pthread['counter'])
    if cesubloc.header['counter'] == pthread['counter']:
        pass
        #print ("<INPUT_OUTPUT>", "  cesubloc['counter'] == pthread['counter']: =", pthread['counter'], "   (output[", pio, "] inchangée)")
    else:
        cesubloc.header['counter'] = pthread['counter']
        try:
            pebloc.c_exebloc_recup_inputs(pieb, pthread)
            #print ("<INPUT_OUTPUT>", f" inputs[0]=bloc_name={cesubloc.inputs[0]['var']},  inputs[1]=output_id={cesubloc.inputs[1]['var']}")
            cesubloc.c_exesubloc_validation_standard()
            find = False
            for thread in list_threads:
                for exe in thread['list_exe']:
                    if exe['run']:
                        #print ("<INPUT_OUTPUT>", f"bloc_name={cesubloc.inputs[0]['var']}, exe['exebloc'].header['name']{exe['exebloc'].header['name']}")
                        if cesubloc.inputs[0]['var'] == exe['exebloc'].header['name']:               # nom du bloc exécuté
                            AB   = exe['exebloc'].header['AB']                      # version du bloc exécuté
                            ibo  = exe['iesubloc']                                  # index du subloc "output"
                            ido  = exe['exebloc'].sublocs[ibo].header['id']         # ID du subloc "output"
                            #print ("<INPUT_OUTPUT>", f"output_id={cesubloc.inputs[1]['var']},  exe['exebloc'].sublocs[ibo].header['id']{ido}")
                            if cesubloc.inputs[1]['var'] == ido:               # nom du bloc exécuté
                                #print ("<INPUT_OUTPUT>", f"trouvé")
                                find = True
                                cesubloc.outputs[0]['var'] = exe['exebloc'].sublocs[ibo].outputs[0]['var'] 
                                cesubloc.outputs[0]['valide'] = exe['exebloc'].sublocs[ibo].outputs[0]['valide'] and cesubloc.outputs[0]['valide']

            if not find:
                #print ("<INPUT_OUTPUT>", f"pas trouvé")
                cesubloc.outputs[0]['valide'] = False
        except:
            #print ("<INPUT_OUTPUT>", PARAM_TEXT_EXCEPTION)
            for output in cesubloc.outputs:
                output['valide'] = False
        cesubloc.c_exesubloc_overwriting_outputs()
    #print ("<INPUT_OUTPUT> retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    return cesubloc.outputs[pio]['var'], cesubloc.outputs[pio]['valide']

