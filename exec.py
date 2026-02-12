# ATTENTION: la source de ce fichier ce trouve dans le répertoire "Target"
import threading
import inspect
import time
import sys
import math
from pymodbus.client import ModbusTcpClient
from PARAM_NAME_BLOC import *
from c_exebloc import *
from sharedata import list_threads
PARAM_TEXT_EXCEPTION = " EXCEPTION: so output(s) become unvalid"


def recup_procedure(psubloc):
    proc_name = "recupe_procedure: "
    """ ajout l'adresse de la procédure qui correspond au nom du bloc"""
    if   psubloc.header['name'] == PARAM_NAME_BLOC_ADD:          procedure= c_exesubloc_add
    elif psubloc.header['name'] == PARAM_NAME_BLOC_AND:          procedure= c_exesubloc_and
    elif psubloc.header['name'] == PARAM_NAME_BLOC_APPEND:       procedure= c_exesubloc_append
    elif psubloc.header['name'] == PARAM_NAME_BLOC_CABLIN:       procedure= c_exesubloc_cablin
    elif psubloc.header['name'] == PARAM_NAME_BLOC_CABLOUT:      procedure= c_exesubloc_cablout
    elif psubloc.header['name'] == PARAM_NAME_BLOC_CLOCK:        procedure= c_exesubloc_clock
    elif psubloc.header['name'] == PARAM_NAME_BLOC_COMP:         procedure= c_exesubloc_comp
    elif psubloc.header['name'] == PARAM_NAME_BLOC_CONST_PI:     procedure= c_exesubloc_const_pi
    elif psubloc.header['name'] == PARAM_NAME_BLOC_DIFFERENCIAL: procedure= c_exesubloc_differencial
    elif psubloc.header['name'] == PARAM_NAME_BLOC_DELAY:        procedure= c_exesubloc_delay
    elif psubloc.header['name'] == PARAM_NAME_BLOC_DIV:          procedure= c_exesubloc_div
    elif psubloc.header['name'] == PARAM_NAME_BLOC_DT:           procedure= c_exesubloc_dt
    elif psubloc.header['name'] == PARAM_NAME_BLOC_EDGE:         procedure= c_exesubloc_edge
    elif psubloc.header['name'] == PARAM_NAME_BLOC_FILTER_FO:    procedure= c_exesubloc_filter_FO
    elif psubloc.header['name'] == PARAM_NAME_BLOC_GETI:         procedure= c_exesubloc_geti
    elif psubloc.header['name'] == PARAM_NAME_BLOC_INFORMATION:  procedure= c_exesubloc_information
    elif psubloc.header['name'] == PARAM_NAME_BLOC_INPUT:        procedure= c_exesubloc_input
    elif psubloc.header['name'] == PARAM_NAME_BLOC_INPUT_OUTPUT: procedure= c_exesubloc_input_output
    elif psubloc.header['name'] == PARAM_NAME_BLOC_INSERT:       procedure= c_exesubloc_insert
    elif psubloc.header['name'] == PARAM_NAME_BLOC_INTEGRATOR:   procedure= c_exesubloc_integrator
    elif psubloc.header['name'] == PARAM_NAME_BLOC_LEN:          procedure= c_exesubloc_len
    elif psubloc.header['name'] == PARAM_NAME_BLOC_LIMIT:        procedure= c_exesubloc_limit
    elif psubloc.header['name'] == PARAM_NAME_BLOC_MEMORY:       procedure= c_exesubloc_memory
    elif psubloc.header['name'] == PARAM_NAME_BLOC_MINMAX:       procedure= c_exesubloc_minmax
    elif psubloc.header['name'] == PARAM_NAME_BLOC_MODBUS_CONN:  procedure= c_exesubloc_modbus_conn
    elif psubloc.header['name'] == PARAM_NAME_BLOC_MODBUS_READ:  procedure= c_exesubloc_modbus_read
    elif psubloc.header['name'] == PARAM_NAME_BLOC_MODBUS_WRITE: procedure= c_exesubloc_modbus_write
    elif psubloc.header['name'] == PARAM_NAME_BLOC_MULT:         procedure= c_exesubloc_mult
    elif psubloc.header['name'] == PARAM_NAME_BLOC_NOT:          procedure= c_exesubloc_not
    elif psubloc.header['name'] == PARAM_NAME_BLOC_OR:           procedure= c_exesubloc_or
    elif psubloc.header['name'] == PARAM_NAME_BLOC_OUTPUT:       procedure= c_exesubloc_output
    elif psubloc.header['name'] == PARAM_NAME_BLOC_PREVIOUS:     procedure= c_exesubloc_previous
    elif psubloc.header['name'] == PARAM_NAME_BLOC_POP:          procedure= c_exesubloc_pop
    elif psubloc.header['name'] == PARAM_NAME_BLOC_PUTI:         procedure= c_exesubloc_puti
    elif psubloc.header['name'] == PARAM_NAME_BLOC_RANGE:        procedure= c_exesubloc_range
    elif psubloc.header['name'] == PARAM_NAME_BLOC_SELECT:       procedure= c_exesubloc_select
    elif psubloc.header['name'] == PARAM_NAME_BLOC_SUB:          procedure= c_exesubloc_sub
    elif psubloc.header['name'] == PARAM_NAME_BLOC_TIME:         procedure= c_exesubloc_time
    elif psubloc.header['name'] == PARAM_NAME_BLOC_TYPE:         procedure= c_exesubloc_type
    elif psubloc.header['name'] == PARAM_NAME_BLOC_VALIDREAD:    procedure= c_exesubloc_validRead
    elif psubloc.header['name'] == PARAM_NAME_BLOC_VALIDWRITE:   procedure= c_exesubloc_validWrite
    else:
        print (proc_name, "❌ERROR: function not defined for this bloc <"+psubloc.header['name']+">")
    return procedure


def c_exesubloc_add (pebloc, pieb, pio, pthread):
    """ exécution du bloc ADDITION (dans la boucler écurcive)"""
    cesubloc = pebloc.sublocs[pieb]
    #print ("<ADD> les paramètres reçus sont: pieb=", pieb, ",   pio=", pio, ",   counter=", pthread['counter'])
    if cesubloc.header['counter'] == pthread['counter']:
        pass
        #print ("<ADD>", "  cesubloc['counter'] == pthread['counter']: =", pthread['counter'], "   (output[", pio, "] inchangée)")
    else:
        cesubloc.header['counter'] = pthread['counter']
        try: #if True: #try:
            pebloc.c_exebloc_recup_inputs(pieb, pthread)
            cesubloc.c_exesubloc_validation_standard()
            cesubloc.outputs[0]['var'] = cesubloc.inputs[0]['var'] + cesubloc.inputs[1]['var']
        except: #else: #except:
            print ("<ADD>", PARAM_TEXT_EXCEPTION)
            for output in cesubloc.outputs:
                output['valide'] = False
        cesubloc.c_exesubloc_overwriting_outputs()
    #print ("<ADD> retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    return cesubloc.outputs[pio]
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
            print ("<AND>", PARAM_TEXT_EXCEPTION)
            for output in cesubloc.outputs:
                output['valide'] = False
        cesubloc.c_exesubloc_overwriting_outputs()
    #print ("<AND> retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    return cesubloc.outputs[pio]
def c_exesubloc_append (pebloc, pieb, pio, pthread):
    """ exécution de la fonction append() de python (dans la boucle récurcive)"""
    # les index des IOs
    #I_LIST = 0
    #I_ELEM = 1
    #O_LIST = 0
    cesubloc = pebloc.sublocs[pieb]
    #print ("<append> les paramètres sont: pieb=", pieb, ",   pio=", pio, ",   counter=", pthread['counter'])
    if cesubloc.header['counter'] == pthread['counter']:
        pass
        #print ("<append>", "  cesubloc['counter'] == pthread['counter']: =", pthread['counter'], "   (output[", pio, "] inchangée)")
    else:
        cesubloc.header['counter'] = pthread['counter']
        try:
            pebloc.c_exebloc_recup_inputs(pieb, pthread)
            cesubloc.c_exesubloc_validation_standard()
            cesubloc.inputs[0]['var'].append(cesubloc.inputs[1]['var'])
            cesubloc.outputs[0]['var'] = cesubloc.inputs[0]['var']
        except:
            print ("<append>", PARAM_TEXT_EXCEPTION)
            for output in cesubloc.outputs:
                output['valide'] = False
        cesubloc.c_exesubloc_overwriting_outputs()
    #print ("<append> retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    return cesubloc.outputs[pio]
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
            print ("<CABLIN>", PARAM_TEXT_EXCEPTION)
            for output in cesubloc.outputs:
                output['valide'] = False
        cesubloc.c_exesubloc_overwriting_outputs()
    #print ("<CABLIN> retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    if 'forced' in cesubloc.outputs[pio]:
        cesubloc.outputs[pio]['var'] = cesubloc.outputs[pio]['forced_value']
        cesubloc.outputs[pio]['valide'] = cesubloc.outputs[pio]['forced_valide']
    return cesubloc.outputs[pio]
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
            print ("<CABLOUT>", PARAM_TEXT_EXCEPTION)
            for output in cesubloc.outputs:
                output['valide'] = False
        cesubloc.c_exesubloc_overwriting_outputs()
    #print ("<CABLOUT> retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    return cesubloc.outputs[pio]
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
            print ("<CLOCK>", PARAM_TEXT_EXCEPTION)
            for output in cesubloc.outputs:
                output['valide'] = False
        cesubloc.c_exesubloc_overwriting_outputs()
    #print ("<CLOCK> retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    return cesubloc.outputs[pio]
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
            print ("<COMP>", PARAM_TEXT_EXCEPTION)
            for output in cesubloc.outputs:
                output['valide'] = False
    #print ("<COMP> retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    return cesubloc.outputs[pio]
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
            print ("<CONST_PI>", PARAM_TEXT_EXCEPTION)
            for output in cesubloc.outputs:
                output['valide'] = False
        cesubloc.c_exesubloc_overwriting_outputs()
    #print ("<CONST_PI> retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    return cesubloc.outputs[pio]
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
            print ("<DELAY>", PARAM_TEXT_EXCEPTION)
            for output in cesubloc.outputs:
                output['valide'] = False
        cesubloc.c_exesubloc_overwriting_outputs()
    #print ("<DELAY> retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    return cesubloc.outputs[pio]
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
            if cesubloc.outputs[1]['valide']:
                cesubloc.outputs[0]['var'] = (cesubloc.inputs[0]['var'] - cesubloc.outputs[1]['var']) / pthread['cycle_time']
            else:
                cesubloc.outputs[0]['var'] = 0               
            cesubloc.outputs[0]['valide'] = cesubloc.inputs[0]['valide'] and cesubloc.outputs[1]['valide'] 
            cesubloc.outputs[1]['var'] = cesubloc.inputs[0]['var']
            cesubloc.outputs[1]['valide'] = cesubloc.inputs[0]['valide']
        except:
            print ("<DIFF>", PARAM_TEXT_EXCEPTION)
            for output in cesubloc.outputs:
                output['valide'] = False
        cesubloc.c_exesubloc_overwriting_outputs()
    #print ("<DIFFERENCIAL> retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    return cesubloc.outputs[pio]
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
            print ("<DIV>", PARAM_TEXT_EXCEPTION)
            for output in cesubloc.outputs:
                output['valide'] = False
        cesubloc.c_exesubloc_overwriting_outputs()
    #print ("<DIV> retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    return cesubloc.outputs[pio]
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
            print ("<DT>", PARAM_TEXT_EXCEPTION)
            for output in cesubloc.outputs:
                output['valide'] = False
        cesubloc.c_exesubloc_overwriting_outputs()
    #print ("<DT> retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    return cesubloc.outputs[pio]
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
            print ("<EDGE>", PARAM_TEXT_EXCEPTION)
            for output in cesubloc.outputs:
                output['valide'] = False
        cesubloc.c_exesubloc_overwriting_outputs()
    #print ("<EDGE> retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    return cesubloc.outputs[pio]
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
            print ("<FILTER_FO>", PARAM_TEXT_EXCEPTION)
            for output in cesubloc.outputs:
                output['valide'] = False
        cesubloc.c_exesubloc_overwriting_outputs()
    #print ("<FILTER_FO> retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    return cesubloc.outputs[pio]
def c_exesubloc_geti (pebloc, pieb, pio, pthread):
    """ exécution de: récupération d'un element d'une liste, string, tuple (dans la boucle récurcive)"""
    # les index des IOs
    #I_LIST = 0
    #I_INDEX =1
    #O_ELEM = 0
    cesubloc = pebloc.sublocs[pieb]
    #print ("<geti> les paramètres sont: pieb=", pieb, ",   pio=", pio, ",   counter=", pthread['counter'])
    if cesubloc.header['counter'] == pthread['counter']:
        pass
        #print ("<geti>", "  cesubloc['counter'] == pthread['counter']: =", pthread['counter'], "   (output[", pio, "] inchangée)")
    else:
        cesubloc.header['counter'] = pthread['counter']
        try:
            pebloc.c_exebloc_recup_inputs(pieb, pthread)
            cesubloc.c_exesubloc_validation_standard()
            cesubloc.outputs[0]['var'] = cesubloc.inputs[0]['var'][cesubloc.inputs[1]['var']]
        except:
            print ("<geti>", PARAM_TEXT_EXCEPTION)
            for output in cesubloc.outputs:
                output['valide'] = False
        cesubloc.c_exesubloc_overwriting_outputs()
    #print ("<geti> retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    return cesubloc.outputs[pio]
def c_exesubloc_information (pebloc, pieb, pio, pthread):
    """ exécution du bloc INFORMATION: lecture des infos d'une variable"""
    # les index des IO
    #I_IN = 0
    #O_id = 0
    #O_name = 1
    #O_comment = 2
    #O_local_name = 3
    #O_local_comment = 4
    cesubloc = pebloc.sublocs[pieb]
    #print ("<INFORMATION> les paramètres sont: pieb=", pieb, ",   pio=", pio, ",   counter=", pthread['counter'])
    if cesubloc.header['counter'] == pthread['counter']:
        pass
        #print ("<INFORMATION>", "cesubloc['counter'] == pthread['counter']: =", pthread['counter'], "   (output[", pio, "] inchangée)")
    else:
        cesubloc.header['counter'] = pthread['counter']
        try:
            prevout = pebloc.c_exebloc_recup_input (pieb, pthread, 0)
            cesubloc.outputs[0]['var'] = prevout['id']
            cesubloc.outputs[1]['var'] = prevout['name']
            cesubloc.outputs[2]['var'] = prevout['comment']
            if 'local_name' in prevout:
                cesubloc.outputs[3]['var'] = prevout['local_name']
            if 'local_comment' in prevout:
                cesubloc.outputs[4]['var'] = prevout['local_comment']
            cesubloc.outputs[0]['valide'] = True
            cesubloc.outputs[1]['valide'] = True
            cesubloc.outputs[2]['valide'] = True
            cesubloc.outputs[3]['valide'] = 'local_name' in prevout
            cesubloc.outputs[4]['valide'] = 'local_comment' in prevout
        except:
            print ("<DIFF>", PARAM_TEXT_EXCEPTION)
            for output in cesubloc.outputs:
                output['valide'] = False
        cesubloc.c_exesubloc_overwriting_outputs()
    #print ("<INFORMATION> retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    return cesubloc.outputs[pio]
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
            print ("<INPUT>", PARAM_TEXT_EXCEPTION)
            cesubloc.outputs[0]['valide'] = False
        cesubloc.c_exesubloc_overwriting_outputs()
    #print ("<INPUT> retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    #return cesubloc.outputs[pio]['var'], cesubloc.outputs[pio]['valide']
    return cesubloc.outputs[pio]
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
                                if cesubloc.inputs[0]['valide'] and cesubloc.inputs[1]['valide']:
                                    cesubloc.outputs[0]['valide'] = exe['exebloc'].sublocs[ibo].outputs[0]['valide']
                                else: 
                                    cesubloc.outputs[0]['valide'] = False
            if not find:
                #print ("<INPUT_OUTPUT>", f"pas trouvé")
                cesubloc.outputs[0]['valide'] = False
        except:
            print ("<INPUT_OUTPUT>", PARAM_TEXT_EXCEPTION)
            for output in cesubloc.outputs:
                output['valide'] = False
        cesubloc.c_exesubloc_overwriting_outputs()
    #print ("<INPUT_OUTPUT> retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    return cesubloc.outputs[pio]
def c_exesubloc_insert (pebloc, pieb, pio, pthread):
    """ exécution de la fonction insert() de python (dans la boucle récurcive)"""
    # les index des IOs
    #I_LIST = 0
    #I_INDEX =1
    #I_ELEM = 2
    #O_LIST = 0
    cesubloc = pebloc.sublocs[pieb]
    #print ("<insert> les paramètres sont: pieb=", pieb, ",   pio=", pio, ",   counter=", pthread['counter'])
    if cesubloc.header['counter'] == pthread['counter']:
        pass
        #print ("<insert>", "  cesubloc['counter'] == pthread['counter']: =", pthread['counter'], "   (output[", pio, "] inchangée)")
    else:
        cesubloc.header['counter'] = pthread['counter']
        try:
            pebloc.c_exebloc_recup_inputs(pieb, pthread)
            cesubloc.c_exesubloc_validation_standard()
            cesubloc.outputs[0]['var'] = cesubloc.inputs[0]['var'].insert(cesubloc.inputs[1]['var'], cesubloc.inputs[2]['var'])
        except:
            print ("<insert>", PARAM_TEXT_EXCEPTION)
            for output in cesubloc.outputs:
                output['valide'] = False
        cesubloc.c_exesubloc_overwriting_outputs()
    #print ("<insert> retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    return cesubloc.outputs[pio]
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
            if cesubloc.inputs[I_TAU]['var'] > 0:
                delta = (cesubloc.inputs[I_IN]['var'] * pthread['cycle_time']) / cesubloc.inputs[I_TAU]['var']
            else:
                delta = cesubloc.inputs[I_IN]['var']
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
            print ("<INTEGRATOR>", PARAM_TEXT_EXCEPTION)
            for output in cesubloc.outputs:
                output['valide'] = False
        cesubloc.c_exesubloc_overwriting_outputs()
    #print ("<INTEGRATOR> retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    return cesubloc.outputs[pio]
def c_exesubloc_len (pebloc, pieb, pio, pthread):
    """ exécution de la méthode len() de python (dans la boucle récurcive)"""
    # les index des IOs
    #I_IN = 0
    #O_LEN = 0
    cesubloc = pebloc.sublocs[pieb]
    #print ("<len> les paramètres sont: pieb=", pieb, ",   pio=", pio, ",   counter=", pthread['counter'])
    if cesubloc.header['counter'] == pthread['counter']:
        pass
        #print ("<len>", "  cesubloc['counter'] == pthread['counter']: =", pthread['counter'], "   (output[", pio, "] inchangée)")
    else:
        cesubloc.header['counter'] = pthread['counter']
        try:
            pebloc.c_exebloc_recup_input(pieb, pthread, 0)
            #cesubloc.c_exesubloc_validation_standard()
            cesubloc.outputs[0]['valide'] = cesubloc.inputs[0]['valide']
            cesubloc.outputs[0]['var'] = len(cesubloc.inputs[0]['var'])
        except:
            print ("<len>", PARAM_TEXT_EXCEPTION)
            for output in cesubloc.outputs:
                output['valide'] = False
        cesubloc.c_exesubloc_overwriting_outputs()
    #print ("<len> retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    return cesubloc.outputs[pio]
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
            print ("<LIMIT>", PARAM_TEXT_EXCEPTION)
            for output in cesubloc.outputs:
                output['valide'] = False
        cesubloc.c_exesubloc_overwriting_outputs()
    #print ("<LIMIT>", " LIMIT retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    return cesubloc.outputs[pio]
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
            print ("<MEMORY>", PARAM_TEXT_EXCEPTION)
            for output in cesubloc.outputs:
                output['valide'] = False
        cesubloc.c_exesubloc_overwriting_outputs()
    #print ("<MEMORY> retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    return cesubloc.outputs[pio]
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
            print ("<MINMAX>", PARAM_TEXT_EXCEPTION)
            for output in cesubloc.outputs:
                output['valide'] = False
        cesubloc.c_exesubloc_overwriting_outputs()
    #print ("<MINMAX> retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    return cesubloc.outputs[pio]

def c_exesubloc_modbus_conn(pebloc, pieb, pio, pthread):
    """ exécution du bloc de connection ModBus/TCP (dans la boucler écurcive)"""
    # les index des IOs
    #I_@IP = 0
    #I_PORT = 1
    #I_TIMEOUT = 2
    #I_CLOSE = 3
    #O_ID = 0
    #O_CONNECTED = 0
    def modbus_connection():
        proc_name = "mod_bus_connection: "
        #print (proc_name, f"début")
        #ret_client = ModbusTcpClient('127.0.0.1', port=502, timeout=0.2)  # IP esclave
        ret_client = ModbusTcpClient(host=cesubloc.inputs[0]['var'], port=cesubloc.inputs[1]['var'], timeout=cesubloc.inputs[2]['var']) #, retries=0
        #print (proc_name, f"après client.ModbusTcpClient(),  client={ret_client}")
        ret_client.connect()
        #print (proc_name, f"après client.connect(),  client={ret_client}")
        return ret_client

    cesubloc = pebloc.sublocs[pieb]
    #print (f"<MODBUS_CONN>---début---name={cesubloc.outputs[pio]['name']}: les paramètres reçus sont: pieb={pieb},   pio={pio},   counter={pthread['counter']}")
    if cesubloc.header['counter'] == pthread['counter']:
        #print ("<MODBUS_CONN> pas d'exécution: cesubloc['counter'] == pthread['counter']: =", pthread['counter'], "   (output[", pio, "] inchangée)")
        pass
    else:
        cesubloc.header['counter'] = pthread['counter']
        #print (f"<MODBUS_CONN> exécution:  cesubloc.header['counter']{cesubloc.header['counter']},   pthread['counter']:{pthread['counter']}")
        try:
            pebloc.c_exebloc_recup_inputs(pieb, pthread)
            cesubloc.c_exesubloc_validation_standard()
            #print (f"<MODBUS_CONN> après validation standard")
            #for i, input in enumerate(cesubloc.inputs): print (f"<MODBUS_CONN> les entrées [{i}]: name={input['name']},  validité={input['valide']},  value={input['var']}")
            #for i, output in enumerate(cesubloc.outputs): print (f"<MODBUS_CONN> les sorties [{i}]: name={output['name']},  validité={output['valide']},  value={output['var']}")
            #cesubloc.outputs[0]['var'] = "ID"
            #cesubloc.outputs[1]['var'] = True
            if hasattr(cesubloc.outputs[0]['var'], "connected"):
                #print (f"<MODBUS_CONN> ID.connected existe,   cesubloc.outputs[0]['var'].connected={cesubloc.outputs[0]['var'].connected}")
                connected_exist = True
            else:
                #print (f"<MODBUS_CONN> ID.connected n'existe pas,   cesubloc.outputs[0]['var']={cesubloc.outputs[0]['var']}")
                connected_exist = False
            if cesubloc.inputs[3]['var']:
                #print (f"<MODBUS_CONN> demande CLOSE,   cesubloc.outputs[0]['var']={cesubloc.outputs[0]['var']}")
                if connected_exist:
                    #print (f"<MODBUS_CONN> demande CLOSE et connected existe,   cesubloc.outputs[0]['var']={cesubloc.outputs[0]['var']}")
                    if cesubloc.outputs[0]['var'].connected:
                        #print (f"<MODBUS_CONN> demande CLOSE et connected==True,   cesubloc.outputs[0]['var']={cesubloc.outputs[0]['var']}")
                        cesubloc.outputs[0]['var'].close()
                        cesubloc.outputs[1]['var'] = cesubloc.outputs[0]['var'].connected
                    else:
                        #print (f"<MODBUS_CONN> demande CLOSE et connected==False,   cesubloc.outputs[0]['var']={cesubloc.outputs[0]['var']}")
                        cesubloc.outputs[0]['var'] = None
                        cesubloc.outputs[1]['var'] = False
                else:
                    #print (f"<MODBUS_CONN> demande CLOSE et connected n'existe pas,   cesubloc.outputs[0]['var']={cesubloc.outputs[0]['var']}")
                    cesubloc.outputs[0]['var'] = None
                    cesubloc.outputs[1]['var'] = False
            else:
                #print (f"<MODBUS_CONN> il n'y a pas de demande de fermeture de la connexion cesubloc.outputs[0]['var']={cesubloc.outputs[0]['var']}")
                if connected_exist:
                    #print (f"<MODBUS_CONN>  .connected existe={cesubloc.outputs[0]['var'].connected}")
                    if cesubloc.outputs[0]['var'].connected:
                        #print (f"<MODBUS_CONN> déjà connected ne rien faire")
                        #return cesubloc.outputs[0]['var']
                        pass
                    else:
                        #print (f"<MODBUS_CONN> not connected 1")
                        client = modbus_connection()
                        #print (f"<MODBUS_CONN> aprés connexion 1, client={client},  .connected={client.connected}")
                        cesubloc.outputs[0]['var'] = client
                        cesubloc.outputs[1]['var'] = client.connected
                else:
                    #print (f"<MODBUS_CONN> not connected 2")
                    client = modbus_connection()
                    #print (f"<MODBUS_CONN> aprés connxion 2, client={client}  .connected={client.connected}")
                    cesubloc.outputs[0]['var'] = client
                    cesubloc.outputs[1]['var'] = client.connected
        except:
            print ("<MODBUS_CONN>", PARAM_TEXT_EXCEPTION)
            for output in cesubloc.outputs:
                output['valide'] = False
        cesubloc.c_exesubloc_overwriting_outputs()
        #for i, output in enumerate(cesubloc.outputs): print (f"<MODBUS_CONN> les sorties [{i}]: name={output['name']},  validité={output['valide']},  value={output['var']}")
    #print (f"<MODBUS_CONN>---fin---name={cesubloc.outputs[pio]['name']}: retourne l'output [{pio}]: var={cesubloc.outputs[pio]['var']}, val={cesubloc.outputs[pio]['valide']}")
    return cesubloc.outputs[pio]

def c_exesubloc_modbus_read (pebloc, pieb, pio, pthread):
    """ exécution du bloc de connection ModBus/TCP (dans la boucler écurcive)"""
    # les index des IOs
    #I_ID = 0
    #I_SALVE = 1
    #I_FONCTION =2
    #I_@OFFSET = 3
    #I_COUNT = 4
    #O_VALUE = 0
    #O_STATUS = 1
    cesubloc = pebloc.sublocs[pieb]
    #print (f"<MODBUS_READ>---début---name={cesubloc.outputs[pio]['name']}: les paramètres reçus sont: pieb={pieb},   pio={pio},   counter={pthread['counter']}")
    if cesubloc.header['counter'] == pthread['counter']:
        #print ("<MODBUS_READ>", " pas d'exécution: cesubloc['counter'] == pthread['counter']: =", pthread['counter'], "   (output[", pio, "] inchangée)")
        pass
    else:
        cesubloc.header['counter'] = pthread['counter']
        #print ("<MODBUS_READ>", f" exécution:  cesubloc.header['counter']{cesubloc.header['counter']},   pthread['counter']:{pthread['counter']}")
        try:
            pebloc.c_exebloc_recup_inputs(pieb, pthread)
            cesubloc.c_exesubloc_validation_standard()
            #print (f"<MODBUS_READ> après validation standard")
            #for i, input in enumerate(cesubloc.inputs): print (f"<MODBUS_READ> les entrées [{i}]: name={input['name']},  validité={input['valide']},  value={input['var']}")
            if hasattr(cesubloc.inputs[0]['var'], "connected"):
                #print (f"<MODBUS_READ> ID.connected existe,   cesubloc.outputs[0]['var'].connected={cesubloc.inputs[0]['var'].connected}")
                connected_exist = True
            else:
                #print (f"<MODBUS_READ> ID.connected n'existe pas,   cesubloc.outputs[0]['var']={cesubloc.inputs[0]['var']}")
                connected_exist = False
            if connected_exist:
                if cesubloc.inputs[0]['var'].connected:
                    if cesubloc.inputs[2]['var']==3: #n° de fonction
                        read_result = cesubloc.inputs[0]['var'].read_holding_registers(cesubloc.inputs[3]['var'], cesubloc.inputs[4]['var'], slave=cesubloc.inputs[1]['var'])
                        if read_result.isError():
                            #cesubloc.outputs[0]['var'] = None
                            cesubloc.outputs[0]['valide'] = False
                            cesubloc.outputs[1]['var'] = read_result
                            #print(f"❌ <MODBUS_READ>  read error:  ErrorCode={read_result}")
                        else:
                            #print(f"✅ <MODBUS_READ> read OK: length={len(read_result.registers)}")
                            cesubloc.outputs[0]['var'] = read_result.registers
                            cesubloc.outputs[1]['var'] = 0 # status ok
                else:
                    #print(f"<MODBUS_READ>  client not connected")
                    #cesubloc.outputs[0]['var'] = None
                    cesubloc.outputs[0]['valide'] = False
                    cesubloc.outputs[1]['var'] = -1 #status: not connected
                    cesubloc.outputs[1]['valide'] = True
            else:
                #print(f"<MODBUS_READ>  client not connected")
                #cesubloc.outputs[0]['var'] = None
                cesubloc.outputs[0]['valide'] = False
                cesubloc.outputs[1]['var'] = -1 #status: not connected
                cesubloc.outputs[1]['valide'] = True
        except:
            print ("<MODBUS_READ>", PARAM_TEXT_EXCEPTION)
            for output in cesubloc.outputs:
                output['valide'] = False
        cesubloc.c_exesubloc_overwriting_outputs()
        #for i, output in enumerate(cesubloc.outputs): print (f"<MODBUS_READ> les sorties [{i}]: name={output['name']},  validité={output['valide']},  value={output['var']}")
    #print (f"<MODBUS_READ>---fin---name={cesubloc.outputs[pio]['name']}: retourne l'output [{pio}]: var={cesubloc.outputs[pio]['var']}, val={cesubloc.outputs[pio]['valide']}")
    return cesubloc.outputs[pio]

def c_exesubloc_modbus_write (pebloc, pieb, pio, pthread):
    """ exécution du bloc d'écriture ModBus/TCP (dans la boucler écurcive)"""
    # les index des IOs
    #I_ID = 0
    #I_SALVE = 1
    #I_FONCTION =2
    #I_@OFFSET = 3
    #I_VALUE = 4
    #O_valide = 0
    #O_STATUS = 1
    cesubloc = pebloc.sublocs[pieb]
    #print (f"<MODBUS_WRITE>---début---name={cesubloc.outputs[pio]['name']}: les paramètres reçus sont: pieb={pieb},   pio={pio},   counter={pthread['counter']}")
    if cesubloc.header['counter'] == pthread['counter']:
        #print ("<MODBUS_WRITE>", " pas d'exécution: cesubloc['counter'] == pthread['counter']: =", pthread['counter'], "   (output[", pio, "] inchangée)")
        pass
    else:
        cesubloc.header['counter'] = pthread['counter']
        #print ("<MODBUS_WRITE>", f" exécution:  cesubloc.header['counter']{cesubloc.header['counter']},   pthread['counter']:{pthread['counter']}")
        if 1: #try:
            pebloc.c_exebloc_recup_inputs(pieb, pthread)
            cesubloc.c_exesubloc_validation_standard()
            #print (f"<MODBUS_WRITE> après validation standard")
            #for i, input in enumerate(cesubloc.inputs): print (f"<MODBUS_WRITE> les entrées [{i}]: name={input['name']},  validité={input['valide']},  value={input['var']}")
            if cesubloc.inputs[0]['var'].connected:
                if cesubloc.inputs[2]['var']==16: #n° de fonction
                    write_result = cesubloc.inputs[0]['var'].write_registers(cesubloc.inputs[3]['var'], cesubloc.inputs[4]['var'], slave=cesubloc.inputs[1]['var'])
                    if write_result.isError():
                        cesubloc.outputs[0]['var'] = False
                        #print(f"❌ <MODBUS_WRITE>  write error:  ErrorCode={write_result}")
                    else:
                        #print(f"✅ <MODBUS_WRITE> write OK: length={len(write_result.registers)}")
                        cesubloc.outputs[0]['var'] = True
                    cesubloc.outputs[1]['var'] = write_result.function_code
            else:
                #print(f"<MODBUS_WRITE>  client not connected")
                cesubloc.outputs[0]['var'] = False
                cesubloc.outputs[1]['var'] = -1 #status: not connected
        else: #except:
            print ("<MODBUS_WRITE>", PARAM_TEXT_EXCEPTION)
            for output in cesubloc.outputs:
                output['valide'] = False
        cesubloc.c_exesubloc_overwriting_outputs()
        #for i, output in enumerate(cesubloc.outputs): print (f"<MODBUS_WRITE> les sorties [{i}]: name={output['name']},  validité={output['valide']},  value={output['var']}")
    #print (f"<MODBUS_WRITE>---fin---name={cesubloc.outputs[pio]['name']} retourne l'output [{pio}]: var={cesubloc.outputs[pio]['var']}, val={cesubloc.outputs[pio]['valide']}")
    return cesubloc.outputs[pio]

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
            print ("<MULT>", PARAM_TEXT_EXCEPTION)
            for output in cesubloc.outputs:
                output['valide'] = False
        cesubloc.c_exesubloc_overwriting_outputs()
    #print ("<MUL> retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    return cesubloc.outputs[pio]
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
            print ("<NOT>", PARAM_TEXT_EXCEPTION)
            for output in cesubloc.outputs:
                output['valide'] = False
        cesubloc.c_exesubloc_overwriting_outputs()
    #print ("<NOT> retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    return cesubloc.outputs[pio]
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
            print ("<OR>", PARAM_TEXT_EXCEPTION)
            for output in cesubloc.outputs:
                output['valide'] = False
        cesubloc.c_exesubloc_overwriting_outputs()
    #print ("<OR> retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    return cesubloc.outputs[pio]
def c_exesubloc_output (pebloc, pieb, pio, pthread):
    """ exécution du bloc OUTPUT (dans la boucler écurcive)"""
    cesubloc = pebloc.sublocs[pieb]
    #print (f"<OUTPUT>---début---name={cesubloc.outputs[pio]['name']}: les paramètres reçus sont: pieb={pieb},   pio={pio},   counter={pthread['counter']}")
    if cesubloc.header['counter'] == pthread['counter']:
        pass
        #print ("cesubloc['counter'] == pthread['counter']: =", pthread['counter'], "   (output[", pio, "] inchangée)")
    else:
        cesubloc.header['counter'] = pthread['counter']
        try: #if True: #try:
            pebloc.c_exebloc_recup_input(pieb, pthread, 0)
            #cesubloc.c_exesubloc_validation_standard()
            #for i, input in enumerate(cesubloc.inputs): print (f"<OUTPUT> les entrées [{i}]: name={input['name']},  validité={input['valide']},  value={input['var']}")

            cesubloc.outputs[0]['var']    = cesubloc.inputs[0]['var']
            cesubloc.outputs[0]['valide'] = cesubloc.inputs[0]['valide']
        except: #else: #except:
            print ("<OUTPUT>", PARAM_TEXT_EXCEPTION)
            cesubloc.outputs[0]['valide'] = False
        cesubloc.c_exesubloc_overwriting_outputs()
    #for i, output in enumerate(cesubloc.outputs): print (f"<OUTPUT> les sorties [{i}]: name={output['name']},  validité={output['valide']},  value={output['var']}")
    #print (f"<OUTPUT>---fin---name={cesubloc.outputs[pio]['name']} retourne l'output [{pio}]: var={cesubloc.outputs[pio]['var']}, val={cesubloc.outputs[pio]['valide']}")
    return cesubloc.outputs[pio]
def c_exesubloc_pop (pebloc, pieb, pio, pthread):
    """ exécution de la fonction pop() de python (dans la boucle récurcive)"""
    # les index des IOs
    #I_LIST = 0
    #I_INDEX =1
    #O_LIST = 0
    #O_ELEM = 1
    cesubloc = pebloc.sublocs[pieb]
    #print ("<pop> les paramètres sont: pieb=", pieb, ",   pio=", pio, ",   counter=", pthread['counter'])
    if cesubloc.header['counter'] == pthread['counter']:
        pass
        #print ("<pop>", "  cesubloc['counter'] == pthread['counter']: =", pthread['counter'], "   (output[", pio, "] inchangée)")
    else:
        cesubloc.header['counter'] = pthread['counter']
        try:
            pebloc.c_exebloc_recup_inputs(pieb, pthread)
            cesubloc.c_exesubloc_validation_standard()
            cesubloc.outputs[1]['var'] = cesubloc.inputs[0]['var'].pop(cesubloc.inputs[1]['var'])
            cesubloc.outputs[0]['var'] = cesubloc.inputs[0]['var']
        except:
            print ("<pop>", PARAM_TEXT_EXCEPTION)
            for output in cesubloc.outputs:
                output['valide'] = False
        cesubloc.c_exesubloc_overwriting_outputs()
    #print ("<pop> retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    return cesubloc.outputs[pio]
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
                print ("<PREVIOUS>", PARAM_TEXT_EXCEPTION)
                for output in cesubloc.outputs:
                    output['valide'] = False
            cesubloc.c_exesubloc_overwriting_outputs()
        #print ("<PREVIOUS> retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    return cesubloc.outputs[pio]
def c_exesubloc_puti (pebloc, pieb, pio, pthread):
    """ exécution de la fonction qui affecte un élément d'une liste (dans la boucle récurcive)"""
    # les index des IOs
    #I_LIST = 0
    #I_INDEX =1
    #I_ELEM = 2
    #O_LIST = 0
    cesubloc = pebloc.sublocs[pieb]
    #print ("<puti> les paramètres sont: pieb=", pieb, ",   pio=", pio, ",   counter=", pthread['counter'])
    if cesubloc.header['counter'] == pthread['counter']:
        pass
        #print ("<puti>", "  cesubloc['counter'] == pthread['counter']: =", pthread['counter'], "   (output[", pio, "] inchangée)")
    else:
        cesubloc.header['counter'] = pthread['counter']
        try:
            pebloc.c_exebloc_recup_inputs(pieb, pthread)
            cesubloc.c_exesubloc_validation_standard()
            cesubloc.inputs[0]['var'][cesubloc.inputs[1]['var']] = cesubloc.inputs[2]['var']
            cesubloc.outputs[0]['var'] = cesubloc.inputs[0]['var']
        except:
            print ("<puti>", PARAM_TEXT_EXCEPTION)
            for output in cesubloc.outputs:
                output['valide'] = False
        cesubloc.c_exesubloc_overwriting_outputs()
    #print ("<puti> retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    return cesubloc.outputs[pio]
def c_exesubloc_range (pebloc, pieb, pio, pthread):
    """ exécution de la fonction range() de python (dans la boucle récurcive)"""
    # les index des IOs
    #I_START = 0
    #I_STOP = 1
    #I_STEP = 2
    #O_OUT = 0
    cesubloc = pebloc.sublocs[pieb]
    #print ("<range> les paramètres sont: pieb=", pieb, ",   pio=", pio, ",   counter=", pthread['counter'])
    if cesubloc.header['counter'] == pthread['counter']:
        pass
        #print ("<range>", "  cesubloc['counter'] == pthread['counter']: =", pthread['counter'], "   (output[", pio, "] inchangée)")
    else:
        cesubloc.header['counter'] = pthread['counter']
        try:
            pebloc.c_exebloc_recup_inputs(pieb, pthread)
            cesubloc.c_exesubloc_validation_standard()
            cesubloc.outputs[0]['var'] = range(cesubloc.inputs[0]['var'], cesubloc.inputs[1]['var'], cesubloc.inputs[2]['var'])
        except:
            print ("<range>", PARAM_TEXT_EXCEPTION)
            for output in cesubloc.outputs:
                output['valide'] = False
        cesubloc.c_exesubloc_overwriting_outputs()
    #print ("<range> retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    return cesubloc.outputs[pio]
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
            print ("<SELECT>", PARAM_TEXT_EXCEPTION)
            for output in cesubloc.outputs:
                output['valide'] = False
        cesubloc.c_exesubloc_overwriting_outputs()
    #print ("<SELECT> retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    return cesubloc.outputs[pio]
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
            print ("<SUB>", PARAM_TEXT_EXCEPTION)
            for output in cesubloc.outputs:
                output['valide'] = False
        cesubloc.c_exesubloc_overwriting_outputs()
    #print ("<SUB> retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    return cesubloc.outputs[pio]
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
            print ("<TIME>", PARAM_TEXT_EXCEPTION)
            for output in cesubloc.outputs:
                output['valide'] = False
        cesubloc.c_exesubloc_overwriting_outputs()
    #print ("<TIME> retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    return cesubloc.outputs[pio]
def c_exesubloc_type (pebloc, pieb, pio, pthread):
    """ exécution du bloc type: typage explicite d'une variable (dans la boucle récurcive)"""
    cesubloc = pebloc.sublocs[pieb]
    #print ("<TYPE> les paramètres sont: pieb=", pieb, ",   pio=", pio, ",   counter=", pthread['counter'])
    if cesubloc.header['counter'] == pthread['counter']:
        pass
        #print ("<TYPE>", "  cesubloc['counter'] == pthread['counter']: =", pthread['counter'], "   (output[", pio, "] inchangée)")
    else:
        cesubloc.header['counter'] = pthread['counter']
        try:
            pebloc.c_exebloc_recup_inputs(pieb, pthread)
            i_in   = cesubloc.inputs[0]['var']
            i_type = cesubloc.inputs[1]['var']
            cesubloc.c_exesubloc_validation_standard()
            #print (f"<TYPE> I0:{i_in}, I1:{i_type},  O0:{cesubloc.outputs[0]['var']}")
            if i_type == 1:
                #print ("<TYPE==1>: ")
                cesubloc.outputs[0]['var'] = bool(i_in)
            elif i_type == 2:
                #print ("<TYPE==2>: ")
                cesubloc.outputs[0]['var'] = int(i_in)
            elif i_type == 3:
                #print ("<TYPE==3>: ")
                cesubloc.outputs[0]['var'] = float(i_in)
            elif i_type == 4:
                #print ("<TYPE==4>: ")
                cesubloc.outputs[0]['var'] = str(i_in)
            elif i_type == 5:
                #print ("<TYPE==5>: ")
                cesubloc.outputs[0]['var'] = None
            elif i_type == 6:
                #print ("<TYPE==6>: ")
                if i_in is None:
                    cesubloc.outputs[0]['var'] = list()
                else:
                    if isinstance(i_in, int) or isinstance(i_in, float) or isinstance(i_in, bool):
                        cesubloc.outputs[0]['var'] = list([i_in])
                    else:
                        cesubloc.outputs[0]['var'] = list(i_in)
            elif i_type == 7:
                #print ("<TYPE==7>: ")
                if i_in is None:
                    cesubloc.outputs[0]['var'] = tuple()
                else:
                    if isinstance(i_in, int) or isinstance(i_in, float) or isinstance(i_in, bool):
                        cesubloc.outputs[0]['var'] = tuple((i_in))
                    else:
                        cesubloc.outputs[0]['var'] = tuple(i_in)
            elif i_type == 8:
                #print ("<TYPE==8>: ")
                if i_in is None:
                    cesubloc.outputs[0]['var'] = dict()
                else:
                    cesubloc.outputs[0]['var'] = dict(i_in)
            elif i_type == 9:
                #print ("<TYPE==9>: ")
                if i_in is None:
                    cesubloc.outputs[0]['var'] = set()
                else:
                    cesubloc.outputs[0]['var'] = set(i_in)
            else: # pas de coversion de type
                #print ("<TYPE==autre>: ")
                cesubloc.outputs[0]['var'] = i_in
            #print(f"<TYPE>2 O0:{cesubloc.outputs[0]['var']}")

        except:
            print ("<TYPE>3:", PARAM_TEXT_EXCEPTION)
            for output in cesubloc.outputs:
                output['valide'] = False
        cesubloc.c_exesubloc_overwriting_outputs()
    #print ("<TYPE> retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    return cesubloc.outputs[pio]
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
            print ("<VALIDREAD>", PARAM_TEXT_EXCEPTION)
            for output in cesubloc.outputs:
                output['valide'] = False
        cesubloc.c_exesubloc_overwriting_outputs()
    #print ("<VALIREAD> retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    return cesubloc.outputs[pio]
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
            print ("<VALIDWRITE>", PARAM_TEXT_EXCEPTION)
            for output in cesubloc.outputs:
                output['valide'] = False
        cesubloc.c_exesubloc_overwriting_outputs()
    #print ("<VALIDWRITE> retourne l'output [", pio, "]: var=", cesubloc.outputs[pio]['var'], "val=", cesubloc.outputs[pio]['valide'])
    return cesubloc.outputs[pio]
