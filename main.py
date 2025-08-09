#! /usr/bin/python3
import decimal
import threading
import time
import os
import sys
import math
import inspect
import gc
import subprocess
import tkinter.font
#from tkinter import font
from tkinter import *
from tkinter import ttk, filedialog, messagebox
import copy
import pickle
import socket
from datetime import datetime

from module_bloc_file import *
from exec import *
from c_exebloc import *
from PARAM import *
from PARAM_NAME_BLOC import *
from sharedata import *
from clientTCP import *

PARAM_DEBUG_ROUTAGE = False
PARAM_MODE_MONITORING="RT"
PARAM_MODE_EDITION="edit"

flag_monitoring = False
monitoring_thread = None

lien_origine = {}
lien_destination = {}
memo_event_clic_droit=False
memo_event_clic_gauche_header=False
memo_lien_en_cours=False

routage_level=0
compile_level=0
arborescence = "/"
def io_text(io):
    """retourn le texte d'un IO """
    proc_name = "io_text: "
    print (proc_name, f"oi={io}")
    if not 'lien' in io and 'defaut_value' in io:
        print (proc_name, f"pas de lien")
        val = io['defaut_value']
        val = str(val)+PARAM_FLECHE_DROITE
    elif 'initial_value' in io:
        print (proc_name, f"initial value")
        val = io['initial_value']
        val = str(val)+PARAM_ICONE_INITIALISATION
    else:
        val = ""
    if 'event_id' in io:
        for thread in list_threads:
            if io['event_id']== thread['id']:
                #evt= " ("+thread['name']+")"
                evt= " ("+PARAM_ICONE_EVENT+thread['name']+")"
    else:
        if 'local_name' in io:
            name = io['local_name']
        else:
            name = io['name']
        evt = ""
    return val+name+evt

class c_mire:
    """dessine la mire"""
    def __init__(self, can):
        xoff = can.winfo_width() // 2
        yoff = can.winfo_height() // 2
        #zoom(1, xoff, yoff)          # applique le zoom par défaut
        self.param_nb_cercle = 19
        self.param_cercle_couleur= "grey75"
        self.param_croix_couleur= "#FFAAAA"
        self.param_cercle_pas = 2000
        self.param_largeur_trait = 1
        self.cercles = []
        t_mire="mire"
        # dessine la croix au centre
        self.ligne_verticale  = can.create_line(0, -1000000, 0, 1000000, tag=[t_mire, "ligne_verticale"], fill=self.param_croix_couleur)
        self.ligne_horizontale= can.create_line(-1000000, 0, 1000000, 0, tag=[t_mire, "ligne_horizontale"], fill=self.param_croix_couleur)
        # dessine des cercles concentriques
        for i in range(1, self.param_nb_cercle):
            r = i * self.param_cercle_pas
            self.cercles.append (can.create_oval(-r, r, r, -r, tag=[t_mire, "cercles"], outline=self.param_cercle_couleur, width=self.param_largeur_trait))
        # dessine le centre
        self.centre  = can.create_line(0, 0, 1, 1, tag=[t_mire, "centre"], fill="black")
        can.move (ALL, xoff, yoff)        # décale le canvas pour avoir la mire au milieu
        #zoom(0.5, xoff, yoff)          # applique le zoom par défaut
class c_position:
    """structure une position (tule) en position x,y"""
    def __init__(self, posxy):
        self.x = posxy[0]
        self.y = posxy[1]
class c_bloc:
    """ structure un "lebloc"""
    def __init__(self, tk_master):
        """ cré la sturcture principale d'un bloc """
        #self.master = tk_master
        sous_blocs = []
        header = {}
        header['structure_version'] = "2.0"
        header['name'] = "defaut_name"
        header['autor']= "unknow"
        header['organisation'] = "?"
        header['key_word'] = []
        header['key_word'].append("initial")
        header['key_word'].append("test")
        header['key_word'].append("maquette v2")
        header['last_id'] = 0
        self.header = header
        self.sublocs = sous_blocs
    def __repr__(self):
        chaine = "Classs c_bloc: "
        chaine = chaine  + str(self.header) + ""
        for i, elem in enumerate(self.sublocs):
            chaine= chaine + str(self.sublocs[i]) + "\n"
        return chaine
        #return "Class c_bloc: %s " % (self.sublocs)
    def c_bloc_show_title(self, txt):
        global arborescence
        if 'master' in globals():
            #print ('elle existe')
            master.title(txt + arborescence + self.header['name'])
        else:
            print ('elle n''existe pas')
    def c_bloc_set_name(self, name):
        self.header['name']=name
    def c_bloc_set_autor(self, autor):
        self.header['autor']=autor
    def c_bloc_set_organisation(self, organisation):
        self.header['organisation']=organisation
    def init_key_index(self):
        self.key_index = 0
    def c_bloc_set_key(self, key):
        self.header['key_word'][self.key_index]=key
        self.key_index += 1
    def c_bloc_add_key(self, key):
        self.header['key_word'].append(key)
    def c_bloc_set_id(self, id, bidon=0):
        self.header['last_id']=id
    def c_bloc_set_structure(self, bidon1, bidon2=0):
        return
    def c_bloc_position(self, raz=True):
        """trouve le position de chaque BLOC et l'\écrit dans la structure"""
        proc_name = "c_bloc_position: "
        print (proc_name, "début")
        i_index=0
        o_index=0
        for i, elem in enumerate(self.sublocs):
            #print (proc_name, " i=", i,  "cadre ID=", elem.header['id_cadre'], " position=", canvas.coords(elem.header['id_cadre']))
            if raz:
                #print (proc_name, "RAZ")
                pos = (0,0,0,0)
            else:
                #print (proc_name, "pas de RAZ")
                pos = conv(canvas, mire, canvas.coords(elem.header['id_cadre']), de_canvas_vers_mire=1)
                #print (proc_name, "pos=", pos)
            self.sublocs[i].header['position'] = pos
            #print (proc_name, " bloc.sublocs[", i, "].header['position']=", pbloc.sublocs[i].header['position'])
            #print (proc_name, "position convertie/mire=", pbloc.sublocs[i].header['position'])
    def c_bloc_add (self, event, type_bloc):
        """ajoute un elément"""
        proc_name = "c_bloc_add: "
        x0 = event.x
        y0 = event.y
        #print (proc_name, "type=<{}>  x=<{}>  y=<{}>".format(type_bloc, x0, y0))
        x1 = x0 + (scale_factor*300)
        y1 = y0 + (scale_factor*100)
        index=0

        if type_bloc=="in":
            #print (proc_name, "type==in<{}>".format(type_bloc))
            bloc_name = PARAM_CHEMIN_SYSTEM+PARAM_NAME_BLOC_INPUT+".bloc"
        elif type_bloc=="out":
            #print (proc_name, "type==out<{}>".format(type_bloc))
            bloc_name = PARAM_CHEMIN_SYSTEM+PARAM_NAME_BLOC_OUTPUT+".bloc"
        else:
            #print (proc_name, "type==out<{}>".format(type_bloc))
            bloc_name = filedialog.askopenfilename(initialdir= "blocs/"+type_bloc, filetypes = [("Fichiers Bloc", "*.bloc")])

        self.sublocs.append (c_sublocs(bloc_name))
        if self.sublocs[-1].header['name'] == PARAM_NAME_BLOC_OUTPUT:
            print (proc_name, "ajout d'un evenement par défaut ")
            self.sublocs[-1].header['event_id'] = PARAM_DEFAUT_THREAD_ID
        self.sublocs[-1].c_sublocs_draw_bloc(event, scale_factor)
    def c_bloc_draw(self, master, canvas, mire):
        """dessine un bloc """
        global scale_factor
        proc_name = inspect.currentframe().f_code.co_name+": "
        #print (proc_name, "début")
        self.c_bloc_show_title("editing: ")
        for elem in self.sublocs:
            posxy = c_position(conv(canvas, mire, elem.header['position'], de_canvas_vers_mire=0))
            #print (proc_name, "position=", posxy)
            elem.c_sublocs_draw_bloc(posxy, scale_factor)
        for elem in self.sublocs:
            for io in elem.ios:
                if 'lien' in io:
                    #print ("call draw_lien (in, out)")
                    #print ("call draw_lien, in=", io)
                    #print ("call draw_lien, out=", io['lien'])
                    draw_lien(io)
    def c_bloc_del_tkinter_id(self):
        proc_name= "c_bloc_del_tkinter_id :"
        for elem in self.sublocs:
            print (proc_name, "elem=", elem)
            if 'id_cadre' in elem.header:
                del elem.header['id_cadre']
                #nb_collected = gc.collect()
                #print (proc_name, "id_cadre: nbr collected=", nb_collected)
            if 'id_texte' in elem.header:
                del elem.header['id_texte']
                #nb_collected = gc.collect()
                #print (proc_name, "id_texte: nbr collected=", nb_collected)
            elem.c_sublocs_del_tkinter_id()
    def c_bloc_redraw(self):
        global bloc, master, canvas, mire
        self.c_bloc_position(raz=False)
        self.c_bloc_erase_draw()
        self.c_bloc_draw(master, canvas, mire)
    def c_bloc_erase_draw(self):
        """supprimer tous à l'écran, à partir des ID du bloc en cours d'édition"""
        global canvas
        proc_name = inspect.currentframe().f_code.co_name+": "
        #print (proc_name, "début")
        #canvas.delete("all")
        if 'bloc' in globals():
            for i, elem in enumerate(self.sublocs):
                self.sublocs[i].c_sublocs_erase_bloc()
    def c_bloc_copy(self):
        " deepcopy d'une donnée structuré"
        proc_name= "c_bloc_copy:"
        destination =pickle.loads(pickle.dumps(self))
        print (proc_name, "bloc source     :", self)
        print (proc_name, "bloc destination:", destination)
        return destination
    def c_bloc_comp(self, other):
        proc_name= inspect.currentframe().f_code.co_name
        égalité = True
        self_copy = self.c_bloc_copy()
        other_copy = other.c_bloc_copy()
        self_copy.c_bloc_del_tkinter_id()
        other_copy.c_bloc_del_tkinter_id()
        self_copy.c_bloc_position(raz=True)
        other_copy.c_bloc_position(raz=True)
        if self_copy.header == other_copy.header:
            if len(self_copy.sublocs) == len(other_copy.sublocs):
                for ssb, osb in zip(self_copy.sublocs, other_copy.sublocs):
                    if not ssb.c_sublocs_comp(osb):
                        print (proc_name, "io diférent:    bloc<", ssb.header['name'])
                        égalité = False
                        break
            else:
                print (proc_name, "nb subloc diférent:    bloc<", self_copy.header['name'], ">    self=", len(self_copy.sublocs), ">    other=", len(other_copy.sublocs))
                égalité = False
        else:
            print (proc_name, "headers diférent:")
            print (proc_name, "headers diférent:   self=", self_copy.header)
            print (proc_name, "headers diférent:  other=", other_copy.header)
            égalité = False
        return égalité
    def c_bloc_print(self):
        proc_name = "c_bloc_print: "
        print (proc_name, "début v2.0----------------------------------------------------")
        print ("{}  printing bloc= {}".format( proc_name, self.header['name']))
        print ("{}     header= {}".format( proc_name, self.header))
        for i, elem in enumerate(self.sublocs):
            print ("{}     bloc[{}]= {}, id={}, --elem.header={}".format (proc_name, i, elem.header['name'], elem.header['id'], elem.header))
            for j, io in enumerate(elem.ios):
                print ( "{}                              ios[{}]= --{}".format (proc_name, j, io))
        print (proc_name, "fin v2.0-----------------------------------------------------")
    def c_bloc_delete_event (self):
        """ suprime tous les "event" ('event_id') des sous-blocs"""
        for esubloc in self.sublocs:
            if esubloc.header['name'] == PARAM_NAME_BLOC_OUTPUT:
                if 'event_id' in esubloc.header:
                    del esubloc.header['event_id']
class c_sublocs:
    def __init__(self, pbloc_name):
        global bloc
        """crée d'un nouvel element BLOC à partir d'un fichier ---.bloc """
        proc_name = "c_sublos.__init__: "
        header = {}
        ios = []
        bloc_lu = read_bloc (pbloc_name)
        if bloc_lu == None:
            print (proc_name, "ERROR-----------file <", pbloc_name, "> bloc_lu==None")
            raise ValueError("C_sublocs can not be created")
        header['name'] = bloc_lu.header['name']
        header['structure_version'] = bloc_lu.header['structure_version']
        header['autor']= bloc_lu.header['autor']
        header['organisation'] = bloc_lu.header['organisation']
        header['key_word'] = bloc_lu.header['key_word']
        header['id'] = id_generateur()
        for i, elem in enumerate(bloc_lu.sublocs):
            if (elem.header['name']==PARAM_NAME_BLOC_INPUT) or (elem.header['name']==PARAM_NAME_BLOC_OUTPUT):
                print (proc_name, ": elem.header['name]=", elem.header['name'])
                for j, io in enumerate(elem.ios):
                    print (proc_name, ": elem.ios[", j, "]=", io)
                    if ( (io['type']=="in") or (io['type']=="out") ):
                        print (proc_name, ": IO('TYPE']=IN OU OUT,  TYPE=", io['type'])
                        # inversion des Entrées / Sorties
                        if io['type']== "in": typ = "out"
                        elif io['type']== "out": typ = "in"
                        else: print (proc_name, ': ERREUR: l\'objet n\'est ni de type IN ni OUT')
                        sub_obj = {}
                        sub_obj['type']= typ
                        if (bloc_lu.header['name']==PARAM_NAME_BLOC_INPUT): io_nbr = last_io (PARAM_NAME_BLOC_INPUT)
                        elif (bloc_lu.header['name']==PARAM_NAME_BLOC_OUTPUT): io_nbr = last_io (PARAM_NAME_BLOC_OUTPUT)
                        else: io_nbr=""
                        sub_obj['name']= io['name']+io_nbr
                        sub_obj['id']= elem.header['id']
                        if 'defaut_value' in io:
                            print(proc_name, ": récupération de la valeur par défaut: defaut_value")
                            sub_obj['defaut_value']= io['defaut_value']
                        if 'memory' in io:
                            print(proc_name, ": récupération de memory")
                            sub_obj['memory']= io['memory']
                            if 'inital_value' in io:
                                print(proc_name, ": récupération de memory")
                                sub_obj['initial_value']= io['initial_value']
                        ios.append(sub_obj)
        self.header = header
        self.ios = ios
    def __repr__(self):
        chaine = "Classs c_sublocs: "
        chaine += str(self.header)+ ""
        chaine += str(self.ios)+ ""
        return chaine
    def c_sublocs_erase_bloc (self):
        """efface un bloc (à l'écran)"""
        proc_name = "c_sublocs_erase_bloc: "
        #print (proc_name, " header name=", self.header['name'])
        if 'id_cadre' in self.header:
            canvas.delete(self.header['id_cadre'])
            #print (proc_name, "delete id cadre=", self.header['id_cadre'])
        if 'id_texte' in self.header:
            canvas.delete(self.header['id_texte'])
            #print (proc_name, "delete id texte=", self.header['id_texte'])
        for io in self.ios:
            if 'id_cadre' in io:
                canvas.delete(io['id_cadre'])
                #print (proc_name, "delete io cadre  name=", io['name'], "  id_cadre=", io['id_cadre'])
            if 'id_texte' in io:
                canvas.delete(io['id_texte'])
                #print (proc_name, "delete io texte  name=", io['name'], "  id_texte=", io['id_texte'])
            if 'id_lien' in io:
                canvas.delete(io['id_lien'])
                #print (proc_name, "delete io id lien  name=", io['name'], "  id_lien=", io['id_lien'])
    def c_sublocs_draw_bloc (self, event, coeff):
        """dessine un bloc et arme les call_back"""
        def c_sublocs_draw_sub_bloc(sobj, x, y, largeur, hauteur, ptags, color):
            """dessine un IO d'un bloc et arme les call_back"""
            font = ( PARAM_FONT, int(max(1,  coeff * PARAM_FONT_SIZE)))
            tags_cadre = ptags + ("cadre",)
            tags_texte = ptags + ("texte",)
            #print ("tags_texte =", tags_texte)
            sobj['id_cadre'] = canvas.create_rectangle (x, y, x+largeur, y+hauteur, tags=tags_cadre, fill=color)

            sobj['id_texte'] = canvas.create_text (x+largeur/2, y+hauteur/2, text = io_text(sobj), tags=tags_texte, font=font)
        proc_name = "c_sublocs_draw_bloc: "
        largeur = coeff * PARAM_HEADER_LARGEUR
        hauteur = coeff * PARAM_HEADER_HAUTEUR
        font = ( PARAM_FONT, int(max(1,  coeff * PARAM_FONT_SIZE)))
        color = PARAM_COLOR_BG_HEADER_USER
        if "system" in self.header['key_word']: color = PARAM_COLOR_BG_HEADER_SYSTEM
        if self.header['name'] == PARAM_NAME_BLOC_INPUT: color = PARAM_COLOR_BG_HEADER_INPUT
        if self.header['name'] == PARAM_NAME_BLOC_OUTPUT: color = PARAM_COLOR_BG_HEADER_OUTPUT
        c_sublocs_draw_sub_bloc (self.header, event.x, event.y, largeur, hauteur, ("header",), color)
        list_header=[(self.header['id_cadre']) , (self.header['id_texte'])]
        for elem_header in list_header:
            canvas.tag_bind(elem_header, "<Button-3>", self.c_sublocs_event_clic_droit_header)
            canvas.tag_bind(elem_header, "<Button-1>", self.c_sublocs_event_clic_gauche_header)
            canvas.tag_bind(elem_header, "<B1-Motion>", self.c_sublocs_event_glisser_gauche_header)
            canvas.tag_bind(elem_header, "<Double-Button-1>", self.c_sublocs_event_double_clic_gauche_header)
            #canvas.tag_bind(elem_header, "<F1>", self.c_sublocs_event_key_F1) ###???
            #canvas.tag_bind(elem_header, "<Delete>", self.c_sublocs_event_delete_header)###"<Delete>" ne fonctionne pas?
        # dessine les i/o et arme les callback
        yi0 = event.y
        yo0 = event.y
        for i , obj_io in enumerate(self.ios):
            if obj_io['type']=="in":
                xc = event.x
                yi0 += hauteur
                yc = yi0
                color = PARAM_COLOR_BG_INPUT
                #print ("ajout input x={}, y={}".format(xc,yc))
            if obj_io['type']=="out":
                xc = event.x + (coeff * PARAM_HEADER_LARGEUR/2.)
                yo0 += hauteur
                yc = yo0
                if 'memory' in obj_io:
                    color = PARAM_COLOR_BG_MEMORY
                else:
                    color = PARAM_COLOR_BG_OUTPUT
                #print ("ajout output x={}, y={}".format(xc,yc))
            c_sublocs_draw_sub_bloc (obj_io, xc, yc, largeur/2, hauteur, (obj_io['type'],), color)
            list_io=[(self.ios[i]['id_cadre']) , (self.ios[i]['id_texte'])]
            for elem_io in list_io:
                canvas.tag_bind (elem_io, "<Button-1>",  lambda event, io= self.ios[i]: self.c_sublocs_event_clic_gauche_io (event, io))
                #canvas.tag_bind (elem_io, "<Button-3>",  lambda event, io= self.ios[i], type=self.ios[i]['type']: self.c_sublocs_event_clic_droit_io (event, io, type))
                canvas.tag_bind (elem_io, "<Button-3>",  lambda event, io= self.ios[i]: self.c_sublocs_event_clic_droit_io (event, io))
                canvas.tag_bind (elem_io, "<B1-Motion>", lambda event, io= self.ios[i]: self.c_sublocs_event_glisser_gauche_io (event, io))
                canvas.tag_bind (elem_io, "<ButtonRelease-1>", lambda event, io= self.ios[i]: self.c_sublocs_event_release_gauche_io (event, io))
                canvas.tag_bind (elem_io, "<Double-Button-1>", lambda event, io= self.ios[i]: self.c_sublocs_event_double_clic_gauche_io (event, io))
    def c_sublocs_event_clic_droit_header (self, event):
        """call_back: sur evenement"""
        global memo_event_clic_droit
        proc_name = "c_sublocs_event_clic_droit_header: "
        #print (proc_name, "event=", event)
        #print (proc_name, "objet=<{}>".format(self))
        memo_event_clic_droit = TRUE
        self.menu_header = menu_header(event, self)
    def c_sublocs_event_clic_gauche_header (self, event):
        """call_back: sur evenement"""
        proc_name = "c_sublocs_event_clic_gauche_header: "
        #print (proc_name, "event=", event)
        #print (proc_name, "objet=<{}>".format(self))
        self.x_clic_gauche = event.x
        self.y_clic_gauche = event.y
        #print (proc_name, "position clic; x={}, y={}".format(self.x_clic_gauche, self.y_clic_gauche))
    def c_sublocs_event_glisser_gauche_header (self, event):
        """call_back: sur evenement"""
        proc_name = "c_sublocs_event_glisser_gauche_header: "
        #print (proc_name, "event=", event)
        #print (proc_name, "objet=<{}>".format(self))
        for i, obj_io in enumerate(self.ios):
            #print ("io=", obj_io)
            if obj_io['type']=='out':
                #print ("io(avec \"out\")=", obj_io)
                list_liens = find_liens (obj_io)
                #print (proc_name, "find_liens=<{}>".format(list_liens))
                for e in list_liens:
                    canvas.delete(e['id_lien'])
                    draw_lien(e)
                    #draw_lien(e, e['lien'])
        list_obj_a_bouger=[] # liste de ID à déplacer
        list_obj_a_bouger.append(self.header['id_cadre'])
        list_obj_a_bouger.append(self.header['id_texte'])
        for i, obj_io in enumerate (self.ios):
            if 'lien' in obj_io:
                    canvas.delete(obj_io['id_lien'])
                    draw_lien(obj_io)
                    #draw_lien(obj_io, obj_io['lien'])
            list_obj_a_bouger.append(self.ios[i]['id_cadre'])
            list_obj_a_bouger.append(self.ios[i]['id_texte'])
        dx = (event.x - self.x_clic_gauche)
        dy = (event.y - self.y_clic_gauche)
        for ob in list_obj_a_bouger:
            #print (proc_name, "position souris; x={}, y={}".format(event.x, event.y))
            canvas.move(ob, dx, dy)
        self.x_clic_gauche = event.x
        self.y_clic_gauche = event.y
        self.header['position']  = conv(canvas, mire, canvas.coords(self.header['id_cadre']), de_canvas_vers_mire=1)

    #def c_sublocs_event_delete_header (self, event):###
    #    """call_back: sur evenement"""
    #    proc_name = "c_sublocs_event_delete_header: "###
    #    del_bloc(self)###


    def c_sublocs_event_double_clic_gauche_header (self, event):
        """call_back: sur evenement"""
        proc_name = "c_sublocs_event_double_clic_gauche_header: "
        #print (proc_name, "event=", event)
        if not ("system" in self.header['key_word']): # les blocs system ne sont ouvrable en double cliquant sur leur entête
            print (proc_name, "ouverture du bloc (name=", self.header['name'], "dans une autre fenêtre")
            open_bloc_new_window(self.header['name'], self.header['id'], (0,0))
        else:
            print (proc_name, "WARNNING: ouverture du bloc (name=", self.header['name'], "impossible, car c'est un bloc <system>")
    def c_sublocs_event_clic_droit_io (self, event, io):
        """call_back: sur evenement"""
        global memo_event_clic_droit
        proc_name = "c_sublocs_event_clic_droit_io: "
        #print (proc_name, "event=", event)
        memo_event_clic_droit = TRUE
        menu_io(event, io)
    def c_sublocs_event_clic_gauche_io (self, event, io=4):
        """call_back: sur evenement"""
        global lien_origine, memo_lien_en_cours
        proc_name = "c_sublocs_event_clic_gauche_io: "
        #print (proc_name, "event=", event)
        lien_origine['io']= io
        lien_origine['event']= event
        #print (proc_name, "io=", io, " event=", event)
        memo_lien_en_cours = TRUE
    def c_sublocs_event_release_gauche_io (self, event, io=4):
        """call_back: sur evenement"""
        proc_name = "c_sublocs_event_release_gauche_io: "
        #print (proc_name, "event=", event)
        #print (proc_name, "event_realese_gauche_io: ")
        try:
            canvas.delete(self.id_lien_provisoire)
            del self.id_lien_provisoire
            print (proc_name, "canvas.delete(self.id_lien_provisoire")
        except:
            print (proc_name, "ERROR: try to ...canvas.delete(self.id_lien_provisoire")
    def c_sublocs_event_double_clic_gauche_io(self, event, io=4):
        """call_back: sur evenement"""
        proc_name = "c_sublocs_event_double_clic_gauche_io: "
        print (proc_name, "event=", event)
        parent=find_parent(io)
        if not "system" in parent.header['key_word']: # les blocs system ne sont ouvrable en double cliquant sur leurs IO
            open_io_new_window(io)
        else:
            print (proc_name, "ouverture du bloc  name=", parent.header['name'], "impossible")
    def c_sublocs_event_glisser_gauche_io (self, event, io=4):
        global origne_lien
        proc_name = "c_sublocs_event_glisser_gauche_io: "
        #print (proc_name, "event=", event)
        #print (proc_name, "event_glisser_droit_io: a=<{}>".format(io))
        try:
            canvas.delete(self.id_lien_provisoire)
        except: pass
        self.id_lien_provisoire  = canvas.create_line(lien_origine['event'].x, lien_origine['event'].y, event.x, event.y, tag=["lien"], fill="red", width=PARAM_LIEN_WIDTH)
    def c_sublocs_set_name(self, name):
        self.header['name']=name
    def c_sublocs_set_id(self, id):
        self.header['id']=name
    def c_sublocs_set_autor(self, autor):
        self.header['autor']=autor
    def c_sublocs_set_organisation(self, organisation):
        self.header['organisation']=organisation
    def c_sublocs_del_tkinter_id(self):
        proc_name= inspect.currentframe().f_code.co_name
        for io in self.ios:
            if 'id_cadre' in io:
                print (proc_name, "del:io['id_cadre']", io['id_cadre'])
                del io['id_cadre']
                #nb_collected = gc.collect()
                #print (proc_name, "id_cadre: nbr collected=", nb_collected)
            if 'id_texte' in io:
                print (proc_name, "del:io['id_texte']", io['id_texte'])
                del io['id_texte']
                #nb_collected = gc.collect()
                #print (proc_name, "id_texte: nbr collected=", nb_collected)
            if 'id_lien' in io:
                print (proc_name, "del:io['id_lien']", io['id_lien'])
                del io['id_lien']
                #nb_collected = gc.collect()
                #print (proc_name, "id_lien: nbr collected=", nb_collected)
            if 'id_lien_provisoire' in io:
                print (proc_name, "del:io['id_lien_provisoire']", io['id_lien_provisoire'])
                del io['id_lien_provisoire']
    def c_sublocs_comp(self, other):
        proc_name= inspect.currentframe().f_code.co_name
        égalité = True
        if self.header == other.header:
            if len(self.ios) == len(other.ios):
                for s_io, o_io in zip(self.ios, other.ios):
                    if s_io != o_io:
                        print (proc_name, "io diférent:    bloc<", self.header['name'], ">")
                        print (proc_name, "io diférent:     self=", s_io )
                        print (proc_name, "io diférent:    other=", o_io)
                        égalité = False
                        break
            else:
                print (proc_name, "taille ios diférent:    bloc<", self.header['name'], ">    self=", len(self.ios), ">    other=", len(other.ios))
                égalité = False
        else:
            print (proc_name, "headers diférent:    self=", self.header, "    other=", other.header)
            égalité = False
        return égalité
    def init_key_index(self):
        self.key_index = 0
    def c_sublocs_set_key(self, key):
        self.header['key_word'][self.key_index]=key
        self.key_index += 1
    def c_sublocs_add_key(self, key):
        self.header['key_word'].append(key)
    def c_sublocs_set_last_id(self, id, bidon=0):
        self.header['last_id']=id
    def c_sublocs_set_structure(self, bidon1, bidon2=0):
        return
class c_average:
    """structure pour calculer une moyenne au fil de leau"""
    def __init__(self):
        self.nb = 0
        self.sum = 0
    def cal_average (self, value):
        self.sum += value
        self.nb +=1
        return self.sum/self.nb
class c_popup:
    def __init__(self, title, x, y):
        self.popup = Toplevel(master)
        self.popup.wm_attributes("-topmost", True)
        self.popup.geometry("+{}+{}".format (x, y))
        self.popup.title(title)
        self.ligne=0
        self.label=[]
        self.entry=[]
        self.set_proc=[] # méthode servant à modifier une variable de l'entête du bloc
    def c_popup_add_une_propriete(self, texte, param, set_proc):
        proc_name = "c_popup_add_une_propriete: "
        self.label.append (Label(self.popup, text = texte))
        self.entry.append (Entry(self.popup))
        self.entry[self.ligne].delete(0, END)
        self.entry[self.ligne].insert(0, param)
        self.label[self.ligne].grid(row = self.ligne, column = 0)
        self.entry[self.ligne].grid(row = self.ligne, column = 1)
        self.set_proc.append(set_proc)
        retour = self.entry[self.ligne]
        self.ligne += 1
        return retour
    def c_popup_validation(self, obj):
        global bloc
        proc_name = "c_popup_validation:"
        key_i=0
        obj.init_key_index()
        for i, set_proc in enumerate(self.set_proc):
            set_proc(self.entry[i].get())
        bloc.c_bloc_show_title("editing: ")
        self.popup.destroy()
        #print ("{}     header= {}".format( proc_name, bloc.header))

def conv(canvas, mire, xy, de_canvas_vers_mire=1):
    """convertit des coordonnées du repére 'canvas' vers le repére 'mire' et réciproquement"""
    proc_name = "conv: "
    xy_centre = canvas.coords(mire.centre)
    retour = ()
    if de_canvas_vers_mire:
        #print (proc_name, "de_canvas_vers_mire")
        try:
            retour_x = (xy[0] - xy_centre[0]) / scale_factor
            retour_y = (xy[1] - xy_centre[1]) / scale_factor
        except:
            retour_x = 0
            retour_y = 0
        return (retour_x, retour_y)
    else:
        #print (proc_name, "de_mire_vers_canvas")
        retour_x = (scale_factor * xy[0]) + xy_centre[0]
        retour_y = (scale_factor * xy[1]) + xy_centre[1]
        return (retour_x, retour_y)
def id_generateur ():
    global bloc
    proc_name= "id_generateur"
    for elem in bloc.sublocs:
        #print (proc_name, " elem=", elem)
        if elem.header['id'] >= bloc.header['last_id']:
            print (proc_name, "ERRUR: un id est supérieur à last_id", elem.header['id'], ", ", bloc.header['last_id'])
    bloc.header['last_id'] +=1
    print (proc_name, "last_loop_id=", bloc.header['last_id'])
    return bloc.header['last_id']
def type_index(pvariable):
    """ returne le type d'une variable"""
    proc_name = "type_index"
    if (type(pvariable) == float): return 0
    if (type(pvariable) == int): return 1
    if (type(pvariable) == bool): return 2
    if (type(pvariable) == str): return 3
    if (type(pvariable) == decimal.Decimal): return 4
    print (proc_name, "ERROR: unknow type: ", type(pvariable))
            
def find_thread_index(pthreads, pthread_id):
    """ retour l'index du thread correspondant à l'ID"""
    proc_name = "find_thread_index"
    #print (proc_name, ":  liste des threads: (ID à trouver=", pthread_id, ")")
    for i, thread in enumerate(pthreads):
        #print (proc_name, ":   - thread[", i, "] name=", thread['name'], "  période=", thread['period'], "   compteur=", thread['counter'])
        if pthread_id == thread['id']:
            #print (proc_name, "index retouné=", i)
            return i
    print (proc_name, " WARNING thread ID<"+str(pthread_id)+"> non trouvé")
    return None

def find_parent (pio):
    """trouve l'elem contenant l'io (pio)"""
    global bloc
    proc_name = "find_parent: "
    #print (proc_name, "pio=", pio)
    for ib, elem in enumerate(bloc.sublocs):
        #print (proc_name, "elem=", elem)
        for i, io in enumerate(elem.ios):
            #print (proc_name, "io=", io)
            if id(io)==id(pio):
                #print (proc_name, "io==pio  pio:", io)
                #print (proc_name, "io==pio  parent:", bloc.sublocs[ib])
                return bloc.sublocs[ib]
    print (proc_name, "ERREUR:   pio n\'a pas de parent, pio=", pio)
    return None
def find_liens (out):
    """trouve tous les (IO) qui pointent vers un OUT(IO)"""
    global bloc
    proc_name = "find_liens: "
    liens=[]
    for ib, elem in enumerate(bloc.sublocs):
        #print (proc_name, "elem=",bloc)
        #print (proc_name, "ib=", ib)
        for i, io in enumerate(elem.ios):
            #print (proc_name, "        i=", i)
            #print (proc_name, "    io=", io)
            if io['type']=='in':
                #print (proc_name, "        c'est un input io=", io)
                if 'lien' in io:
                    index_parent = find_index_bloc (bloc, io['lien']['id_parent'])
                    index_io = find_index_io (bloc.sublocs[index_parent], io['lien']['id_io'])
                    if id(bloc.sublocs[index_parent].ios[index_io]) == id(out):
                        liens.append(bloc.sublocs[ib].ios[i])
    #print (proc_name, "liste des io=", liens)
    return liens
def find_cadre(x,y):
    """trouve l'ID du cadre de type "in" ou "out" en position x,y"""
    proc_name = "find_cadre: "
    items = canvas.find_overlapping(x-PARAM_NEAR, y-PARAM_NEAR, x+PARAM_NEAR, y+PARAM_NEAR)
    #print (proc_name, " item=",items)
    for item in items:
        tags= canvas.gettags(item)
        #print (proc_name, " item=",item, " tags=", tags)
        if (("in" or "out") and "cadre") in tags:
            #print (proc_name, "en x:",x, " y:", y, " item=", item, " tags=", tags)
            return item
    #print (proc_name, "ERREUR: en x:",x, " y:", y, " cadre introuvable")
    return None
def find_bloc_io(id_cadre):
    """trouve l'adresse du "IO" correspondant à un ID de cadre"""
    global bloc
    for ib, elem in enumerate(bloc.sublocs):
        #print ("elem=",bloc)
        for i, io in enumerate(elem.ios):
            #print ("io=", io)
            if io['id_cadre']==id_cadre:
                #print ("find_bloc: cadre trouvé en:", sublocs[ib])
                return bloc.sublocs[ib].ios[i]
def find_position_io(io):
    """trouve la position (tule (x,y)) d'un ID"""
    global scale_factor
    proc_name ="find_position_io: "
    posxy = canvas.coords (io['id_cadre'])
    #print (proc_name, "posxy=", posxy)
    if io['type']=='in':
        position_x = posxy[0]
    else:
        position_x = posxy[0] + scale_factor * PARAM_HEADER_LARGEUR/2
    position_y = posxy[1] + scale_factor * PARAM_HEADER_HAUTEUR/2
    return (position_x, position_y)
def find_index_bloc(pbloc, id):
    """ retourn l'index du sous-bloc correspondant à l'id du sous-bloc"""
    proc_name = "find_index_bloc: "
    index = None
    for i, subloc in enumerate(pbloc.sublocs):
        if subloc.header['id']==id:
            index= i
            break
    if index == None:
        print (proc_name, "ERREUR: l'index <", id, "> n'a pas été trouvé dans le bloc=", pbloc)
    return index
def find_index_io(pelem, id):
    """ retourne l'index d'un IO correspondant à l'id de l'IO"""
    proc_name = "find_index_IO: "
    index = None
    #print (proc_name, "pelem=", pelem)
    for i, tmp_io in enumerate(pelem.ios):
        #print (proc_name, "i=", i, "tmp_io=", tmp_io)
        if tmp_io['id']==id:
            index= i
            #print (proc_name, "id=", id, "trouvé i=", i, "dans tmp_io=", tmp_io)
            break
    if index == None:
        print (proc_name, "ERREUR: l'index <", id, "> n'a pas été trouvé dans le sous_bloc=", pelem)
    return index

def draw_lien(io_in):
    """dessine un lien entre 2 IO"""
    global bloc
    proc_name= "draw_lien: "
    index_parent = find_index_bloc (bloc, io_in['lien']['id_parent'])
    #print (proc_name, "index_parent=", index_parent)
    index_io = find_index_io (bloc.sublocs[index_parent], io_in['lien']['id_io'])
    #print (proc_name, "index_io=", index_io)
    pos_in = find_position_io (io_in)
    io_out = bloc.sublocs[index_parent].ios[index_io]
    pos_out = find_position_io (io_out)
    #print (proc_name, "draw_lien: pos_in=", pos_in, "pos_out=", pos_out)
    if find_parent(io_out).header['name'] == PARAM_NAME_BLOC_PREVIOUS and 'memory' in io_out:
        color = PARAM_COLOR_LINK_LOOP
    #elif find_parent(io_out).header['name'] == PARAM_NAME_BLOC_BREAK and 'memory' in io_out:
    #    color = PARAM_COLOR_LINK_BREAK
    else:
        color = PARAM_COLOR_LINK_STANDARD [io_out['id']%PARAM_COLOR_LINK_MODULO]
        #print (proc_name, "COLOR=", color, "    id=", io_out['id'])

    points = []
    points.append(pos_in[0])
    points.append(pos_in[1])

    points.append(pos_in[0]-scale_factor*PARAM_LIEN_MARGE_X)
    points.append(pos_in[1])

    if pos_out[0] > pos_in[0]: #lien arrière
        if abs(pos_out[1]-pos_in[1]) < scale_factor*PARAM_LIEN_BACKLOOP_Y:
            dy_in = dy_out = -scale_factor*PARAM_LIEN_BACKLOOP_Y
        elif abs(pos_in[1] < pos_out[1]):
            dy_out = -scale_factor*PARAM_LIEN_BACKLOOP_Y
            dy_in  = scale_factor*PARAM_LIEN_BACKLOOP_Y
        else:
            dy_out =  scale_factor*PARAM_LIEN_BACKLOOP_Y
            dy_in  = -scale_factor*PARAM_LIEN_BACKLOOP_Y
        points.append(pos_in[0]-scale_factor*PARAM_LIEN_MARGE_X)
        points.append(pos_in[1]+dy_in)

        points.append(pos_out[0]+scale_factor*PARAM_LIEN_MARGE_X)
        points.append(pos_out[1]+dy_out)
    else:  #lien avant
        if (pos_in[0] - pos_out[0] > scale_factor*PARAM_LIEN_LENGTH_X) and (pos_in[1]-pos_out[1] < scale_factor*4*PARAM_ROUTAGE_IO_DY): # lien avant long
            points.append((pos_in[0]+pos_out[0])/2)
            points.append(pos_in[1]+scale_factor*4*PARAM_ROUTAGE_IO_DY)

        elif abs(pos_out[1]-pos_in[1]) < scale_factor*PARAM_LIEN_ZIGZAG/2:
            distance_x = (pos_in[0]-scale_factor*PARAM_LIEN_MARGE_X)-(pos_out[0]+scale_factor*PARAM_LIEN_MARGE_X)
            points.append(pos_in[0] - scale_factor*PARAM_LIEN_MARGE_X - distance_x/3)
            points.append((pos_in[1]+pos_out[1])/2+scale_factor*PARAM_LIEN_ZIGZAG)

            points.append(pos_out[0]+scale_factor*PARAM_LIEN_MARGE_X+ distance_x/3)
            points.append((pos_in[1]+pos_out[1])/2-scale_factor*PARAM_LIEN_ZIGZAG)

    points.append(pos_out[0]+scale_factor*PARAM_LIEN_MARGE_X)
    points.append(pos_out[1])

    points.append(pos_out[0])
    points.append(pos_out[1])

    io_in['id_lien'] = canvas.create_line(points, smooth=True, tag=["lien"], fill=color, width=PARAM_LIEN_WIDTH)
    #io_in['id_lien'] = canvas.create_line(pos_in[0], pos_in[1], pos_out[0], pos_out[1], tag=["lien"], fill=color, width=3)
def routage ():
    """callback: sur evenement"""

    def routage_pass1(elem, pos):
        """Récurcif: position les elements par rapport à l'element aval"""
        global bloc, routage_level
        routage_level += 1
        if PARAM_DEBUG_ROUTAGE:
            trace_txt = trace_proc(elem, inspect.currentframe().f_code.co_name, routage_level)
            print (trace_txt, "début:----paramètres reçus:  elem=<<<", elem.header['name'], ">>>  (id=", elem.header['id'], "),  position=(", (pos.x, pos.y), ")")
        elem.header['position'] = (pos.x, pos.y)
        if PARAM_DEBUG_ROUTAGE: print (trace_txt, ">>> affectation de header['position']=",elem.header['position'])
        x_amont = pos.x - PARAM_ROUTAGE_DX
        if PARAM_DEBUG_ROUTAGE: print (trace_txt, "x_amont=", x_amont)
        for i, io in enumerate(elem.ios):
            if PARAM_DEBUG_ROUTAGE: print (trace_txt, "boucle ois[", i, "]    io_name=", io['name'],   "    io_type=", io['type'], "    (id=", io['id'], ")")
            if io['type']=='in':
                if 'lien' in io:
                    if PARAM_DEBUG_ROUTAGE: print (trace_txt, "il y a un io['lien'] dans l'io name=", io['name'], ", id=", io['id'], ", id_parent=", io['lien']['id_parent'], ", id_io=", io['lien']['id_io'])
                    index_parent = find_index_bloc (bloc, io['lien']['id_parent'])
                    index_io = find_index_io (bloc.sublocs[index_parent], io['lien']['id_io'])
                    if PARAM_DEBUG_ROUTAGE: print (trace_txt, "le bloc parent est:", bloc.sublocs[index_parent].header['name'], ", (id=", bloc.sublocs[index_parent].header['id'], ")")
                    if bloc.sublocs[index_parent].header['position'][0] >= 0: #parent en position (0,0)
                        if PARAM_DEBUG_ROUTAGE: print (trace_txt, "le parent n'a pas encore été positinné")
                        nb_input  = 0
                        nb_output = 0
                        for j, parent_io in enumerate (bloc.sublocs[index_parent].ios):
                            if parent_io['type'] == 'in':  nb_input  += 1
                            if parent_io['type'] == 'out': nb_output += 1
                        if PARAM_DEBUG_ROUTAGE: print (trace_txt, "nbr input dans parent=", nb_input)
                        if PARAM_DEBUG_ROUTAGE: print (trace_txt, "nbr output dans parent=", nb_output)
                        pos.x = x_amont
                        mem_pos_y = 1*pos.y
                        if PARAM_DEBUG_ROUTAGE: print (trace_txt, "modif pos.x=", pos.x)
                        hauteur_bloc_parent = PARAM_ROUTAGE_MARGE_DY + PARAM_ROUTAGE_HEADER_DY + max (nb_input * PARAM_ROUTAGE_IO_DY, nb_output * PARAM_ROUTAGE_IO_DY)
                        if PARAM_DEBUG_ROUTAGE: print (trace_txt, " hauteur du bloc parent=", hauteur_bloc_parent)
                        routage_pass1(bloc.sublocs[index_parent], pos) ############### récurcivité #####################
                        if PARAM_DEBUG_ROUTAGE: print (trace_txt, "posxy après routage_pass1: x=", pos.x, "y=", pos.y)
                        pos.y = max (pos.y, mem_pos_y + hauteur_bloc_parent)
                        if PARAM_DEBUG_ROUTAGE: print (trace_txt, "affectation posxy: x=", pos.x, "y=", pos.y)
                        routage_level -= 1
                    else:
                        if PARAM_DEBUG_ROUTAGE: print (trace_txt, " le parent a déjà été positinné")
                else:
                    if PARAM_DEBUG_ROUTAGE: print (trace_txt, " pas de input avec un lien")
                        #pos.y += PARAM_ROUTAGE_HEADER_DY
        if PARAM_DEBUG_ROUTAGE: print (proc_name, "FIN---------------------")
    def routage_gravite():
        """Repositionne les elements par rapport au centre de gravité"""
        global bloc
        ox=c_average()
        oy=c_average()
        proc_name = "routage_gravite: "
        for i, elem in enumerate(bloc.sublocs):
            #print (proc_name, " elem scruté pour calcule moyene=", elem)
            gx = ox.cal_average(elem.header['position'][0])
            gy = oy.cal_average(elem.header['position'][1])
        if PARAM_DEBUG_ROUTAGE: print (proc_name, " garivté x=", gx)
        if PARAM_DEBUG_ROUTAGE: print (proc_name, " garivté y=", gy)
        for i, elem in enumerate(bloc.sublocs):
            #print (proc_name, " elem scruté pour recentrage=", elem)
            elem.header['position'] = (elem.header['position'][0]-gx, elem.header['position'][1]-gy)
    global bloc, routage_level
    proc_name = "routage: "
    if not ("system" in bloc.header['key_word']):
        posxy_init = c_position( [0,0])
        #print (proc_name,"début du routage")
        bloc.c_bloc_position(raz=True)
        posxy_init.x = -PARAM_ROUTAGE_DX
        posxy_init.y = 0
        routage_level=0
        posxy_routage = posxy_init
        list_previous_id=[]
        for i, elem in enumerate(bloc.sublocs):
            #print (proc_name, "boucle i=", i, "elem scruté: name=", elem.header['name'], "id=", elem.header['id'])
            if elem.header['name'] == PARAM_NAME_BLOC_OUTPUT:
                if PARAM_DEBUG_ROUTAGE: print (proc_name, "----------------> un output trouvé: call routage_pass1 (name=", elem.header['name'], "(id=", elem.header['id'], "), pos=", (posxy_routage.x, posxy_routage.y) )
                routage_pass1(elem, posxy_routage) # récurcif
                posxy_routage.x = -PARAM_ROUTAGE_DX
                posxy_routage.y += PARAM_ROUTAGE_MARGE_DY + PARAM_ROUTAGE_HEADER_DY + PARAM_ROUTAGE_IO_DY + PARAM_ROUTAGE_OUTPUT_DY
        routage_gravite()
        bloc.c_bloc_erase_draw()
        bloc.c_bloc_draw(master, canvas, mire)
    #print (proc_name,"fin du routage")

def open_bloc_new_window(name, id, pos):
    """ouvre un autre interpréteur Python pour permettre d'éditer le bloc passé en paramètre"""
    global arborescence, flag_monitoring
    proc_name= "open_bloc_new_window: "
    print (proc_name, "bloc name=<{}>".format(name))
    print (proc_name, "position=<{}>".format(pos))
    #f_name= add_point_bloc_to_file_name(name)
    if flag_monitoring: monitoring_str = PARAM_MODE_MONITORING
    else: monitoring_str = PARAM_MODE_EDITION
    #if name==None: name=""
    #subprocess.Popen([sys.executable, "main.py", name, str(config_window['pos_x']), str(config_window['pos_y']), monitoring_str, str(-pos[0]), str(-pos[1]), arborescence + bloc.header['name'] + "/(" + str(id) + ")"])
    if name==None:
        subprocess.Popen([sys.executable, "main.py", str(config_window['pos_x']), str(config_window['pos_y'])])
    else:
        subprocess.Popen([sys.executable, "main.py", str(config_window['pos_x']), str(config_window['pos_y']), name, monitoring_str, str(-pos[0]), str(-pos[1]), arborescence + bloc.header['name'] + "/(" + str(id) + ")"])
def open_io_new_window(io):
    """ouvre un autre interpréteur Python pour permettre d'éditer le bloc passé en paramètre"""
    proc_name = "open_io_new_window: "
    #print (proc_name, "io=", io)
    #print (proc_name, "io['id']=", io['id'])
    id = io['id']
    elem = find_parent(io)
    #print (proc_name, "elem.header=", elem.header)
    print (proc_name, "name du parent=", elem.header['name'])
    name = elem.header['name']
    tmp_bloc = read_bloc (nom_complet_fichier(name, "system" in elem.header['key_word']))
    index = find_index_bloc(tmp_bloc, id)
    print (proc_name, "index=", index)
    pos = tmp_bloc.sublocs[index].header['position']
    print (proc_name, "position/mire de io=", pos)
    open_bloc_new_window(elem.header['name'], elem.header['id'], pos)# (elem.header['name'], elem.header['name'], pos)
def del_bloc(elem):
    """supprime un bloc et les lien associés"""
    global bloc
    proc_name= "del_bloc: "
    #print (proc_name, "objet=<{}>".format(elem))
    canvas.delete(elem.header['id_cadre'])
    canvas.delete(elem.header['id_texte'])
    for io in elem.ios:
        canvas.delete(io['id_cadre'])
        canvas.delete(io['id_texte'])
        if 'lien' in io:
            canvas.delete(io['id_lien'])
        list_lien_vers_outs = find_liens (io)
        #print (proc_name, "\"in\" pointant(s) vers les \"out\" du bloc à détruire", list_lien_vers_outs)
        for io_out in list_lien_vers_outs:
            canvas.delete(io_out['id_lien'])
            del io_out['lien']
    #print (proc_name, "elem=", elem)
    #print (proc_name, "elem id<{}>".format(id(elem)))
    for i, e in enumerate(bloc.sublocs):
        #print (proc_name, "scrutation des élements (i=<{}>) avant suppression".format(i))
        #print (proc_name, "boucle sublocs<{}>".format(id(sublocs[i])))
        if id(bloc.sublocs[i])==id(elem):
            #print (proc_name, "suppression de l\'element <{}>".format(i))
            bloc.sublocs.pop(i)
def update_bloc(elem):
    """mise à jour d'interface d'un bloc et les lien associés"""
    global bloc, canvas
    #proc_name= "update_bloc: "
    proc_name = inspect.currentframe().f_code.co_name
    bloc.c_bloc_position(raz=False)
    mem_liens_in = []
    mem_liens_out = []
    mem_local_names = []
    mem_defaut_values = []
    mem_initial_values = []
    xxxmem_local_defaut_values = []
    mem_events = []
    # lecture du fichier
    bloc_name = add_point_bloc_to_file_name(elem.header['name'])
    bloc_id = elem.header['id']
    #print (proc_name, "bloc_name=<{}>".format(bloc_name))
    if "system" in elem.header['key_word']: chemin = PARAM_CHEMIN_SYSTEM
    else: chemin= PARAM_CHEMIN_USER
    try:
        updated_elem = c_sublocs(le_chemin(bloc_name, "system" in elem.header['key_word'])+bloc_name)
    except ValueError as e:
        print (proc_name, "ERROR-----------file <", elem.header['name'], "> ", e)
        return True
    couple = {}
    if elem.header['name'] == PARAM_NAME_BLOC_OUTPUT:
        if 'event_id' in elem.header:
            couple['id'] = elem.header['id']
            couple['event_id'] = elem.header['event_id']
            mem_events.append(couple)
            print (proc_name, "memo event: couple=", couple)
    for io in elem.ios:
        couple = {}
        if io['type']=='in':
            if 'lien' in io:
                canvas.delete(io['id_lien'])
                couple['id'] = io['id']
                couple['lien'] = io['lien']
                mem_liens_in.append(couple)
                print (proc_name, "memo Couple id/lien \"in\"=id=(", io['id'], ")", couple)
        if io['type']=='out':
            list_out = find_liens(io)
            #print (proc_name, "id de l' io de type out", io['id'])
            #print (proc_name, "liste de io de type out pointés par des liens", list_out)
            if len(list_out) > 0:
                print (proc_name, "liste liens de\"out\"id=(", io['id'], ") liens=", list_out)
                couple['id'] = io['id']
                couple['list_out'] = list_out
                mem_liens_out.append(couple)
                print (proc_name, "memo list_out: couple=", couple)
        if (elem.header['name'] == PARAM_NAME_BLOC_OUTPUT and io['type'] == 'in')\
        or (elem.header['name'] == PARAM_NAME_BLOC_INPUT  and io['type'] == 'out'):
            couple['id'] = io['id']
            couple['xput_name'] = io['name']
            mem_local_names.append(couple)
            print (proc_name, "memo OUTPUT Name: couple=", couple)
        if 'defaut_value' in io and io['type']=='in':###
                couple['id'] = io['id']
                couple['defaut_value'] = io['defaut_value']
                mem_defaut_values.append(couple)
                print (proc_name, "memo defaut_value: couple=", couple)
        if 'local_name' in io:
                couple['id'] = io['id']
                couple['local_name'] = io['local_name']
                mem_local_names.append(couple)
                print (proc_name, "memo Local Name: couple=", couple)
        if 'initial_value' in io and io['type']=='out':###
                couple['id'] = io['id']
                couple['initial_value'] = io['initial_value']
                mem_initial_values.append(couple)
                print (proc_name, "memo initial_value: couple=", couple)
    #print (proc_name, "liste des liens \"in\"=", mem_liens_in)
    #print (proc_name, "liste des liens \"out\"=", mem_liens_out)

    updated_elem.header['id']= bloc_id
    bloc.header['last_id'] -= 1 #pas de nouvel id

    # reposition l'élément au même endroit
    posxy = c_position(conv(canvas, mire, elem.header['position'], de_canvas_vers_mire=0))
    #print (proc_name, "position=", posxy)
    # redirige l'élément vers l'élément updaté
    elem.c_sublocs_erase_bloc()
    elem.header = updated_elem.header
    elem.ios = updated_elem.ios

    #refaire les liens mémorisés
    for i, io in enumerate(elem.ios):
        print (proc_name, "io boucle reconstruction liens: id=", io['id'], " type=", io['type'])
        if io['type']=='in':
            for lien in mem_liens_in:
                if io['id'] == lien['id']:
                    elem.ios[i]['lien'] = lien['lien']
                    #print (proc_name, "reinjection un lien dans l'io=", io)

    if TRUE:
        for lien in mem_liens_out:
            #print (proc_name, "lien dans boucle liens_out, lien=", lien)
            trouve=False
            for i, io in enumerate(elem.ios):
                #print (proc_name, "boucle io,  i=", i)
                if io['type']=='out':
                    #print (proc_name, "io[", i, "] est de type out")
                    if io['id'] == lien['id']:
                        #print (proc_name, "io[", i, "]['id'] égale lien['id']=",lien['id'])
                        #print (proc_name, "trouvé=vrai")
                       trouve=True
                        #for lo in lien['list_out']:
                            #print (proc_name, "list_out dans boucle de lien, list_out=", lo)
                            #if lo['lien'] == elem.ios[i]:
                                #print (proc_name, "ajoute un lien: ", lo, " dans:", elem.ios[i])
            if not trouve:
                for lo in lien['list_out']:
                    del lo['lien']
                    #print (proc_name, "suppression des liens n\'ayant plus d'ID: ", lo)
        for eln in mem_local_names:
            #print (proc_name, "Name dans boucle local_name, name=", eln)
            for i, io in enumerate(elem.ios):
                if io['id'] == eln['id']:
                    if   (elem.header['name'] == PARAM_NAME_BLOC_OUTPUT and io['type'] == 'in')\
                      or (elem.header['name'] == PARAM_NAME_BLOC_INPUT  and io['type'] == 'out'):
                        io['name']=eln['xput_name']
                    else:
                        io['local_name']=eln['local_name']
        for dv in mem_defaut_values:
            print (proc_name, "Défaut Value dans boucle defaut_value, value=", dv)
            for i, io in enumerate(elem.ios):
                if io['id'] == dv['id']:
                    io['defaut_value']=dv['defaut_value']
        for di in mem_initial_values:
            print (proc_name, "Initial Value dans boucle initial_value, value=", di)
            for i, io in enumerate(elem.ios):
                if io['id'] == di['id']:
                    io['initial_value']=di['initial_value']
    for ev in mem_events:
        if elem.header['id'] == ev['id']:
            #io['local_name']=eln['local_name']
            elem.header['event_id']=ev['event_id']


    elem.c_sublocs_draw_bloc(posxy, scale_factor)
    bloc.c_bloc_redraw()
    return False
def last_io (name_type):
    """Retourne le nombre de input ou output du bloc actuellement édité"""
    global bloc
    proc_name = 'last_io: '
    return_value=0
    #print (proc_name, 'début:', 'name_type=', name_type)
    for i, elem in enumerate(bloc.sublocs):
        if (elem.header['name']==name_type): return_value +=1
    #print (proc_name, 'Return_value=', return_value)
    return str(return_value)
def del_lien(io):
    """supprime un lien"""
    global scale_factor
    proc_name = "del_lien: "
    #print (proc_name, f" io=<{io}>")
    if 'lien' in io:
        canvas.delete(io['id_lien'])
        del io['lien']
    txt = io_text(io)
    print (proc_name, f"txt={txt}")
    canvas.itemconfig(io['id_texte'], text=txt)
    #elem = find_parent (io)
    #print (proc_name, f"parent (elem.header)={elem.header}")
    #update_bloc(elem)
def overwriting(io):
    """Forçage d'une entrée ou d'une sortie"""
    print ("OverWritting: io=<{}>".format(io))
    messagebox.showinfo("Warnning", "This function is not yet implemented")
def rename_io(px, py, io):
    """renome une entrée ou une sortie"""
    global bloc
    proc_name = "rename_io: "
    #print (proc_name, "début")
    def proc_null():
        return
    def validation():
        io['name'] = io_name.get()
        pop.popup.destroy()
        bloc.c_bloc_redraw()
    pop = c_popup("io rename", 25+px, 75+py)
    io_name = pop.c_popup_add_une_propriete("Name:", io['name'], proc_null)
    BP_escape = Button(pop.popup, text = 'Escape', width = 25, command = pop.popup.destroy)
    BP_escape.grid(row = pop.ligne, column = 0)
    BP_validation = Button(pop.popup, text='Validation', width = 25, command = validation)
    BP_validation.grid(row = pop.ligne, column = 1)
    #BP_escape.focus()
    BP_validation.bind("<Return>", lambda event: BP_validation.invoke())
    BP_validation.bind("<KP_Enter>", lambda event: BP_validation.invoke())
    BP_escape.bind("<Return>", lambda event: BP_escape.invoke())
    BP_escape.bind("<KP_Enter>", lambda event: BP_escape.invoke())
    #BP_escape.bind("<Escape>", lambda event: BP_escape.invoke())

    pop.entry[0].focus()
    pop.entry[0].bind("<Return>", lambda event: BP_validation.invoke())
    pop.entry[0].bind("<KP_Enter>", lambda event: BP_validation.invoke())

# io paramètres lié à l'instance (local)
def change_local_name_io(px, py, io):
    """renome localement une entrée ou une sortie"""
    global bloc
    proc_name = "change_local_name_io: "
    #print (proc_name, "début")
    def proc_null():
        return
    def validation():
        io['local_name'] = io_name.get()
        pop.popup.destroy()
        bloc.c_bloc_redraw()
    pop = c_popup("io rename", 25+px, 75+py)
    if not 'local_name' in io: io['local_name']="new"
    io_name = pop.c_popup_add_une_propriete("Local Name:", io['local_name'], proc_null)
    BP_escape = Button(pop.popup, text = 'Escape', width = 25, command = pop.popup.destroy)
    BP_escape.grid(row = pop.ligne, column = 0)
    BP_validation = Button(pop.popup, text='Validation', width = 25, command = validation)
    BP_validation.grid(row = pop.ligne, column = 1)
    #BP_escape.focus()
    BP_validation.bind("<Return>", lambda event: BP_validation.invoke())
    BP_validation.bind("<KP_Enter>", lambda event: BP_validation.invoke())
    BP_escape.bind("<Return>", lambda event: BP_escape.invoke())
    BP_escape.bind("<KP_Enter>", lambda event: BP_escape.invoke())
    #BP_escape.bind("<Escape>", lambda event: BP_escape.invoke())

    pop.entry[0].focus()
    pop.entry[0].bind("<Return>", lambda event: BP_validation.invoke())
    pop.entry[0].bind("<KP_Enter>", lambda event: BP_validation.invoke())
def delete_local_name_io(px, py, io):
    """supprime un nom local sur une entrée ou une sortie"""
    global bloc
    proc_name = "delete_local_name_io: "
    del io['local_name']
    bloc.c_bloc_redraw()
def change_initial_value_io(px, py, io):
    """pour definir la valeur par défaut d'une sortie de l'instance"""
    proc_name = "change_initial_value_io: "
    print (proc_name, "début")
    set_defaut_value_io(px, py, io, "initial_value")
def delete_initial_value_io(px, py, io):
    """ supprime la valeur par défaut d'une sortie d'une instance"""
    global bloc
    proc_name = "delete_initial_value_io: "
    print (proc_name, "supprime io['initial_value']=", io['initial_value'])
    del io['initial_value']
    bloc.c_bloc_redraw() #dddddd
def delete_defaut_value_io(px, py, io):
    """ supprime la valeur par défaut d'une entrée"""
    proc_name = "delete_defaut_value_io: "
    print (proc_name, "supprime io['defaut_value']=", io['defaut_value'])
    del io['defaut_value']
def delete_local_defaut_value_io(px, py, io):
    """ supprime la valeur par défaut d'une entrée d'une instance"""
    proc_name = "delete_local_defaut_value_io: "
    print (proc_name, "supprime io['local_defaut_value']=", io['local_defaut_value'])
    del io['local_defaut_value']
def set_defaut_value_io(px, py, io, pdic):
    """pour definir la valeur par défaut d'une entrée"""
    global PARAM_TYPE_LIST
    proc_name = "defaut_value: "
    print (proc_name, f"début: paramêtres: x={px}, y={py}, io={io}, pdic={pdic}, ")
    def proc_null():
        return
    def validation():
        global bloc
        #io['defaut_value'] = float(io_defaut_value.get())
        if combox_type.get() == "float":  io[pdic] = float(io_defaut_value.get())
        if combox_type.get() == "int":    io[pdic] = int(io_defaut_value.get())
        if combox_type.get() == "bool":
            #print (proc_name, " type=BOOL    value brute=",io_defaut_value.get())
            io[pdic] = io_defaut_value.get() == "True" or io_defaut_value.get() == "1"
        if combox_type.get() == "string": io[pdic] = (io_defaut_value.get())

        pop.popup.destroy()
        bloc.c_bloc_redraw()
    pop = c_popup(pdic, 25+px, 75+py)
    if not pdic in io: io[pdic]=0
    io_defaut_value = pop.c_popup_add_une_propriete("Défaut value:", io[pdic], proc_null)
    label_type = Label(pop.popup, text="type:")
    label_type.grid(row = pop.ligne, column = 0)
    combox_type = ttk.Combobox(pop.popup, values=PARAM_TYPE_LIST) #new
    combox_type.set(PARAM_TYPE_LIST[0])
    combox_type.grid(row = pop.ligne, column = 1)
    pop.ligne += 1
    BP_escape = Button(pop.popup, text = 'Escape', width = 25, command = pop.popup.destroy)
    BP_escape.grid(row = pop.ligne, column = 0)
    BP_validation = Button(pop.popup, text='Validation', width = 25, command = validation)
    BP_validation.grid(row = pop.ligne, column = 1)
    #BP_escape.focus()
    BP_validation.bind("<Return>", lambda event: BP_validation.invoke())
    BP_validation.bind("<KP_Enter>", lambda event: BP_validation.invoke())
    BP_escape.bind("<Return>", lambda event: BP_escape.invoke())
    BP_escape.bind("<KP_Enter>", lambda event: BP_escape.invoke())

    pop.entry[0].focus()
    pop.entry[0].bind("<Return>", lambda event: BP_validation.invoke())
    pop.entry[0].bind("<KP_Enter>", lambda event: BP_validation.invoke())
def properties_io(px, py, io):
    """affiche les propriété d'un io"""
    global bloc, PARAM_TYPE_LIST
    def proc_null():
        return
    proc_name = "proterties_io: "
    #print (proc_name, "début")
    pop = c_popup("io info", 25+px, 75+py)
    io_id = pop.c_popup_add_une_propriete("ID:", io['id'], proc_null)
    io_index = pop.c_popup_add_une_propriete("index:", find_index_io(find_parent(io),io['id']), proc_null)
    io_name = pop.c_popup_add_une_propriete("Name:", io['name'], proc_null)
    if 'local_name' in io:
        io_local_name = pop.c_popup_add_une_propriete("Local Name:", io['local_name'], proc_null)
    io_type = pop.c_popup_add_une_propriete("Type:", io['type'], proc_null)
    if 'defaut_value' in io:
        #print (proc_name, "defaut-value type=", type(io['defaut_value']))
        str_type = " ("+PARAM_TYPE_LIST[type_index(io['defaut_value'])]+")"
        io_type = pop.c_popup_add_une_propriete("Defaut value:"+str_type, io['defaut_value'], proc_null)
    if 'local_defaut_value' in io:
        #print (proc_name, "local_defaut-value type=", type(io['local_defaut_value']))
        str_type = " ("+PARAM_TYPE_LIST[type_index(io['local_defaut_value'])]+")"
        io_local_defaut_value = pop.c_popup_add_une_propriete("Local Default Value:"+str_type, io['local_defaut_value'], proc_null)
    if 'memory' in io:
        print (proc_name, "memory=", type(io['memory']))
        str_type = " ("+PARAM_TYPE_LIST[type_index(io['memory'])]+")"
        io_memory = pop.c_popup_add_une_propriete("Memory:"+str_type, io['memory'], proc_null)
    if 'initial_value' in io:
        print (proc_name, "initial value=", type(io['initial_value']))
        str_type = " ("+PARAM_TYPE_LIST[type_index(io['initial_value'])]+")"
        io_init = pop.c_popup_add_une_propriete("Initial:"+str_type, io['initial_value'], proc_null)
    if "lien" in io:
        id_parent = io['lien']['id_parent']
        #print (proc_name, " id parent=:", id_parent)
        id_io = io['lien']['id_io']
        #print (proc_name, " id io=:", id_io)
        index_parent= find_index_bloc(bloc, id_parent)
        parent_header_name = bloc.sublocs[index_parent].header['name']
        parent_header_id = bloc.sublocs[index_parent].header['id']
        parent = find_parent (io['lien'])
        lien_io_id = io['lien']['id_io']
        lien_io_index = find_index_io (bloc.sublocs[index_parent], lien_io_id)
        lien_io_name = bloc.sublocs[index_parent].ios[lien_io_index]['name']
        texte = parent_header_name + "(" + str(parent_header_id) + ") / " + str(lien_io_name) + "(" + str(lien_io_id)+ ")"
        io_lien = pop.c_popup_add_une_propriete("link: (bloc / output)", texte, proc_null)
    BP_escape = Button(pop.popup, text = 'Escape', width = 25, command = pop.popup.destroy)
    BP_escape.grid(row = pop.ligne, column = 0)
def memory_io(add_supp, io):
    """pour definir si une sortie est mémorisable"""
    proc_name= "memory_io: "
    if add_supp == "add":
        io['memory']=True
    elif add_supp == "supp":
        del io['memory']
    else:
        print (procname, "ERROR: Wrong paramater: add_sup is not add or supp")
def capture_add_event(pelem, pthread_id):
    """ajout un événement à un subbloc OUTPUT"""
    def add_event():
        """utlilisation de fonction de captation des paramètre: capture_add_event"""
        global list_threads
        proc_name = "add_event: "
        print (proc_name, "ajout ['event_id'] à <"+pelem.header['name']+">    event_id="+str(pthread_id))
        pelem.header['event_id']= pthread_id
        update_bloc(pelem)
    return add_event
def del_event(pelem):
    del pelem.header['event_id']
    update_bloc(pelem)
def io_interface_position (elem):
    """ retourne la position d'un element (in ou out) dans l'interface """
    global bloc
    proc_name = "move_io: "
    index = find_index_bloc(bloc, elem.header['id'])
    type = elem.header['name']
    #print (proc_name, "type=", type)
    position=0
    nombre=0
    for ib, subloc in enumerate (bloc.sublocs):
        #print (proc_name, "loop1, ib=", ib)
        if bloc.sublocs[ib].header['name']==type:
            nombre += 1
            if ib < index:
                position += 1
    position +=1 #
    #print (proc_name, "position retournée=", position, "nombre=", nombre)
    return position, nombre
def io_interface_move (elem, direction):
    """ monte ou descend un element (in ou out) dans l'interface"""
    global bloc
    proc_name = "io_interface_move: "
    index = find_index_bloc(bloc, elem.header['id'])
    type = elem.header['name']
    print (proc_name, "index=", index)
    precedent=None
    suivant=None
    for ib in range (0, index):
        print (proc_name, "loop1, ib=", ib)
        if bloc.sublocs[ib].header['name']==type:
            precedent = ib
    print (proc_name, "loop1, precedent=", precedent)
    for ib in range (len(bloc.sublocs)-1, index, -1):
        print (proc_name, "loop2, ib=", ib)
        if bloc.sublocs[ib].header['name']==type:
            suivant = ib
    print (proc_name, "loopé, suivant=", suivant)

    if direction=="up":
        print (proc_name, "direction up")
        if precedent != None:
            elem_memo = bloc.sublocs[precedent]
            bloc.sublocs[precedent] = bloc.sublocs[index]
            bloc.sublocs[index] = elem_memo
        else:
            print (proc_name, "io déjà en première position")
    else:
        print (proc_name, "direction down")
        if suivant != None:
            elem_memo = bloc.sublocs[suivant]
            bloc.sublocs[suivant] = bloc.sublocs[index]
            bloc.sublocs[index] = elem_memo
        else:
            print (proc_name, "io déjà en dernière position")
def flip_monitoring():
    global flag_monitoring, monitoring_thread
    flag_monitoring = not flag_monitoring
    if flag_monitoring:
        if clientTCP.socket != None:
            monitoring_thread = threading.Thread(target=monitoring_bloc)
            monitoring_thread.start()
        else:
            messagebox.showinfo("ERROR", "Monitoring not allowed because, the target is not connected via TCP/IP ")
            flag_monitoring = not flag_monitoring
    set_running(flag_monitoring)

def event_deplacement_souris(event):
    """callback: sur evenement"""
    TCPstatus() 
    bar_souris_canv.config(text = "mouse/canv  x:{:5.0f}  y:{:5.0f}".format(event.x, event.y))
    valeur = (event.x, event.y)
    vout = conv (canvas, mire, valeur, de_canvas_vers_mire=1)
    bar_souris_mire.config(text = "mouse/mire x:{:5.2f}  y:{:5.2f}".format(vout[0], vout[1]))
    bar_coeff_zoom.config(text = "Zoom:{:5.3f}".format(scale_factor))
def event_clic_gauche(event):
    """callback: sur evenement"""
    global menu_contxtuel, memo_event_clic_gauche_header
    proc_name = "event_clic_gauche: "
    #print (proc_name, "position event: x={},  y={}".format(event.x, event.y))
    try:
        menu_contextuel.destroy()
    except:
        pass #print (proc_name, "pas de menu contextuel à destroy")
    if memo_event_clic_gauche_header:
        id_cadre = find_cadre(event.x, event.y)
        pos_cadre = canvas.coords(id_cadre)
        tags= canvas.gettags(id_cadre)
        #print (proc_name, "item=", id_cadre, " x=", pos_cadre[0], " y=", pos_cadre[1], "<in>trouvé=", tags)
    memo_event_clic_gauche_header = False
def event_release_gauche(event):
    """callback: sur evenement"""
    global lien_origine, lien_destination
    global memo_lien_en_cours
    def end_error():
        if (lien_origine['io']['type']=='in'):
            start_txt ="INPUT"
            end_txt = "OUTPUT"
        else:
            start_txt ="OUTPUT"
            end_txt = "INPUT"
        print("ERROR: As starting point is an ", start_txt, " the end point must be an ", end_txt)
        messagebox.showinfo("ERROR", "As starting point is an "+start_txt+" the end point must be an "+end_txt)

    proc_name = "event_release_gauche: "
    #print (proc_name, "event=", event)
    if memo_lien_en_cours:
        #lien_origine['pos'] = find_position_io (lien_origine['io'])
        id_cadre = find_cadre(event.x, event.y)
        #print (proc_name, "id_cadre={}".format(id_cadre))
        if id_cadre!=None:
            if id_cadre != lien_origine['io']['id_cadre']: # ...pour libérer le double clic
                #print (proc_name, "id_cadre différent de None")
                lien_destination['id_cadre'] = id_cadre
                #print (proc_name, "id_cadre=", id_cadre)
                lien_destination['io'] = find_bloc_io(id_cadre)
                if ((lien_origine['io'] != None) and (lien_destination['io'] != None)):
                    if     ((lien_origine['io']['type']=='in')  and (lien_destination['io']['type']=='out')) \
                        or ((lien_origine['io']['type']=='out') and (lien_destination['io']['type']=='in' )):
                        if lien_origine['io']['type']=='in':  io_in  = lien_origine['io']
                        if lien_origine['io']['type']=='out': io_out = lien_origine['io']
                        if lien_destination['io']['type']=='in':  io_in  = lien_destination['io']
                        if lien_destination['io']['type']=='out': io_out = lien_destination['io']
                        if ('lien' in io_in):
                            messagebox.showinfo("ERROR", "INPUT can only have one source")
                        else:
                            #print (proc_name, "lin_io_in=", io_in)
                            #print (proc_name, "lin_io_out=", io_out)
                            elem_out = find_parent(io_out)
                            id_parent=  elem_out.header['id']
                            id_io = io_out['id']
                            #ajout le lien vers la output
                            lien ={}
                            lien['id_parent'] = id_parent
                            lien['id_io'] = id_io
                            io_in['lien']= lien
                            draw_lien(io_in)
                            # update pour cacher la valeur par défaut de l'entrée
                            elem = find_parent (io_in)
                            txt = io_text(io_in)
                            print (proc_name, f"txt={txt}")
                            canvas.itemconfig(io_in['id_texte'], text=txt)
                            #update_bloc(elem)
                    else: end_error()
                else: end_error()
        else: end_error()
    memo_lien_en_cours = FALSE
def event_clic_droit(event):
    """callback: sur evenement"""
    global menu_contextuel
    global memo_event_clic_droit
    #print ("event_clic_droit_canvas:")
    #if memo_event_header: print ("memo_event_header=VRAI")
    #else: print ("memo_event_header=FAUX")
    if memo_event_clic_droit==FALSE:
        # crée un menu cntextuel
        x = event.x
        y = event.y
        try:
            menu_contextuel.destroy()
        except:
            pass #print ("pas de menu contextuel à destroy")
        #print ("création menu contextuel en x<{}>  ymc<{}>".format(event.x, event.y))
        items = canvas.find_withtag(CURRENT)
        #print("items len() =<{}>".format(len(items)))
        tags_list = canvas.gettags(items)
        #print ("dans menu, items<{}>   tags<{}".format(items, tags_list))
        menu_contextuel = Menu(master, tearoff=0)
        menu_contextuel.add_command(label = "Add input", command = lambda: bloc.c_bloc_add(event, "in"), background = PARAM_COLOR_BG_HEADER_INPUT, activebackground = PARAM_COLOR_BG_HEADER_INPUT )
        menu_contextuel.add_command(label = "Add output", command = lambda: bloc.c_bloc_add(event, "out"), background = PARAM_COLOR_BG_HEADER_OUTPUT, activebackground = PARAM_COLOR_BG_HEADER_OUTPUT)
        menu_contextuel.add_separator()
        menu_contextuel.add_command(label = "Add system bloc", command = lambda: bloc.c_bloc_add(event, "system"), background = PARAM_COLOR_BG_HEADER_SYSTEM, activebackground = PARAM_COLOR_BG_HEADER_SYSTEM)
        menu_contextuel.add_command(label = "Add user bloc", command = lambda: bloc.c_bloc_add(event, "user"), background = PARAM_COLOR_BG_HEADER_USER, activebackground = PARAM_COLOR_BG_HEADER_USER)
        menu_contextuel.post(event.x_root, event.y_root)
    memo_event_clic_droit = FALSE
def event_clic_molette(event):
    """callback: sur evenement"""
    global x_molette, y_molette
    x_molette = event.x
    y_molette = event.y
    #print ("clic molette: position x={},  y={}".format(event.x, event.y))
def event_deplacement_molette_enfonce(event):
    """callback: sur evenement"""
    global x_molette, y_molette
    canvas.move (ALL, event.x-x_molette, event.y-y_molette)
    #self.canvas.scan_dragto (event.x, event.y, 1)
    event_deplacement_souris(event)
    x_molette = event.x
    y_molette = event.y
def event_molette(event):
    """callback: sur evenement"""
    proc_name = "event_molette: "
    #print (proc_name, "molette pousée ou tirée: position x={},  y={}".format(event.x, event.y))
    event_deplacement_souris(event)
    if sys.platform == "linux":
        if event.num == 4:
            zoom_increment = PARAM_ZOOM_INCREMENT
        elif event.num == 5:
            zoom_increment = 1/PARAM_ZOOM_INCREMENT
        else:
            print (proc_name, "ERROR: mouse well not push or pull")
    else: #windos
        if event.delta>0:
            zoom_increment = PARAM_ZOOM_INCREMENT
        else:
            zoom_increment = 1/PARAM_ZOOM_INCREMENT
    zoom(zoom_increment, event.x, event.y)
#def event_molette_poussee(event):
    #"""callback: sur evenement"""
    ##print ("molette pousée: position x={},  y={}".format(event.x, event.y))
    #event_deplacement_souris(event)
    #zoom(PARAM_ZOOM_INCREMENT, event.x, event.y)
#def event_molette_tiree(event):
    #"""callback: sur evenement"""
    ##print ("molette tirée: position x={},  y={}".format(event.x, event.y))
    #event_deplacement_souris(event)
    #zoom(1/PARAM_ZOOM_INCREMENT, event.x, event.y)
def event_key_space(event):
    """callback: sur evenement"""
    global flag_monitoring
    proc_name = "event_key_space: "
    print (proc_name," arg=", event)
    print (proc_name," KEY_SPACE ")
    flip_monitoring()

def find_bloc_under_event(event):
    """touve le bloc qui est sous le curseur lorsqu'un évenement se produit"""
    global bloc, canvas
    items = canvas.find_all()
    for item in items:
        #print (proc_name, "pour chaque item")
        tags = canvas.gettags(item)
        if tags:
            #print (proc_name, "tags list,  tags=", tags)
            if 'header' in tags:
                print (proc_name, "header in tags,  tags=", tags)
                for elem in bloc.sublocs:
                    print (proc_name, f"pour chaque subloc: elem.header['name']={elem.header['name']}")
                    if elem.header['id_cadre'] == item:
                        print (proc_name, f"elem == item,    elem.header['name']={elem.header['name']}")
                        bbox = canvas.bbox(item)
                        if bbox:
                            x1, y1, x2, y2 = bbox
                            print (proc_name, f"bbox:  x1={x1}, y1={y1}, x2={x2}, y2={y2}")
                            if x1 < event.x and event.x < x2:
                                print (proc_name, f" en x")
                                if y1 < event.y and event.y < y2:
                                    print (proc_name, f" en y")
                                    return elem
    return None
def event_key_F1(event):
    """callback: sur evenement"""
    global bloc, canvas
    proc_name = "event_key_F1: "
    print (proc_name," arg=", event)
    elem = find_bloc_under_event(event)
    if elem != None:
        doc_file = "Documentation/bloc_"+elem.header['name']+".html"
        if os.path.isfile(doc_file):
            print (proc_name, f"nom du fichier d'aide={doc_file}")
            if sys.platform == "linux":
                subprocess.Popen(['xdg-open', doc_file])
            else:
                os.startfile(doc_file)
        else:
         messagebox.showinfo("ERROR", "The ducumentaion is not available for this bloc")
def event_key_F3(event):
    """callback: sur evenement"""
    proc_name = "event_key_F3: "
    print (proc_name," arg=", event)
    print (proc_name," KEY_F3")
    global bloc
    save_file(save_as=False)
    print (proc_name," aprés call save_file")
def event_key_F4(event):
    """callback: sur evenement"""
    proc_name = "event_key_F4: "
    print (proc_name," arg=", event)
    print (proc_name," KEY_F4")
    global bloc
    save_file(save_as=True)
    print (proc_name," aprés call save_file")
def event_key_F5(event):
    """callback: sur evenement"""
    proc_name = "event_key_F5: "
    print (proc_name," arg=", event)
    print (proc_name," KEY_F5")
    global bloc
    update_blocs()
    routage()
def event_key_F7(event):
    """callback: sur evenement"""
    proc_name = "event_key_F7: "
    print (proc_name," arg=", event)
    print (proc_name," KEY_F7")
    routage()
def event_key_delete(event):
    """callback: sur evenement"""
    proc_name = "event_key_delete: "
    print (proc_name," arg=", event)
    elem = find_bloc_under_event(event)
    if elem != None:
        print (proc_name, f"nom du bloc à supprimer={elem.header['name']}")
        del_bloc(elem)
def event_key_escape(event):
    """callback: sur evenement"""
    proc_name = "event_exit: "
    print (proc_name," arg=", event)
    print (proc_name," KEY_Escape")
    on_closing()
def event_redimentionnement_fenetre(event):
    """callback: sur evenement"""
    print ("redimentionnement fenêtre")
    print ("largeur={}, hauteur={}".format(event.width, event.height))
def zoom(factor_brut, x, y):
    """Zoom écran (avec la molette)"""
    global scale_factor, canvas
    proc_name = "zoom: "
    #print(proc_name, "scale_factor=", scale_factor)
    scale = factor_brut * scale_factor
    if (scale > 1.01) :
        print ("zoom max atteint")
    else :
        if (scale < 0.001) :
            print ("zoom min atteint")
        else:
            factor = factor_brut
            scale_factor = scale
            canvas.scale(ALL, x, y, factor, factor)
            #"zoom des textes"
            ltxt = canvas.find_withtag("texte")
            #print (proc_name, "update_font_size: list=<{}>".format(ltxt))
            for i in ltxt:
                new_font = ( PARAM_FONT, int(max(1,  scale_factor * PARAM_FONT_SIZE)))
                canvas.itemconfigure(i, font= new_font)

# Création d'une police personnalisée avec une taille plus grande
def menu_bar():
    global bloc, config_window, rt_menubar, target_menubar, list_compiled, flag_monitoring
    proc_name = "menu_bar: "
    menubar = Menu(master)
    master.config(menu = menubar)
    bloc_menubar = Menu(menubar)
    menubar.add_cascade(label="Bloc", menu = bloc_menubar)
    bloc_menubar.add_command(label = "Open", command = lambda: open_file(None, (0,0)))
    bloc_menubar.add_command(label = "Save [F3]", command = lambda: save_file(save_as=False))
    bloc_menubar.add_command(label = "Save as [F4]", command = lambda: save_file(save_as=True))
    bloc_menubar.add_command(label = "Update [F5]", command = update_blocs)
    bloc_menubar.add_command(label = "Change Properties", command = lambda : properties_header(config_window['pos_x']+10, config_window['pos_y']+10, bloc, modification=1))
    bloc_menubar.add_separator()
    bloc_menubar.add_command(label = "Open new window", command = lambda: open_bloc_new_window(None, "vide", (0,0)))
    bloc_menubar.add_separator()
    bloc_menubar.add_command(label = "Quit [Escape]",  foreground = PARAM_COLOR_MENU_TEXTE_DANGER, activeforeground = PARAM_COLOR_MENU_TEXTE_DANGER, command = on_closing)
    #-------------------------
    #rt_menubar = Menu(menubar)
    #menubar.add_cascade(label = "local (old)", menu = rt_menubar) 
    #menu_RT()
    #-------------------------
    target_menubar = Menu(menubar)
    menubar.add_cascade(label = "Target", menu = target_menubar) 
    menu_target()

    #-------------------------
    edit_menubar = Menu(menubar)
    menubar.add_cascade(label = "Edit", menu = edit_menubar)
    edit_menubar.add_command(label = "Auto layout [F7]", command = routage)
    edit_menubar.add_command(label = "Monitoring (Start/Stop) [Space]", command = flip_monitoring)
    edit_menubar.add_command(label = "Statusbar (show/hide)", command = status_bar)
    #-------------------------
    help_menubar = Menu(menubar)
    menubar.add_cascade(label = "Help", menu = help_menubar)
    help_version_menubar = Menu(help_menubar)
    help_menubar.add_cascade(label = "Version", menu = help_version_menubar)
    help_version_menubar.add_command(label = "bloc editor: Version 1.1")
    help_version_menubar.add_command(label = f"bloc structure: Version {bloc.header['structure_version']}")
    help_mouse_menubar = Menu(help_menubar)
    help_menubar.add_cascade(label = "Mouse usage", menu = help_mouse_menubar)
    help_mouse_menubar.add_command(label = "[Left click] to select, to use menu")
    help_mouse_menubar.add_command(label = "[Left held down] to link, to move")
    help_mouse_menubar.add_command(label = "[Left double-click] to open 'user' bloc")
    help_mouse_menubar.add_command(label = "[Right button] to open the context menu")
    help_mouse_menubar.add_command(label = "[wheel button held down] to scroll within the window")
    help_mouse_menubar.add_command(label = "[wheel rotation] to zoom (in/out)")
    help_key_menubar = Menu(help_menubar)
    help_menubar.add_cascade(label = "Key usage", menu = help_key_menubar)
    help_key_menubar.add_command(label = "[F1] Open the documentation for the bloc whose header is located under the cursor")
    help_key_menubar.add_command(label = "[F3] to save curant bloc")
    help_key_menubar.add_command(label = "[F4] to save curant bloc as")
    help_key_menubar.add_command(label = "[F5] to update curant bloc")
    help_key_menubar.add_command(label = "[F7] to layout curant bloc")
    help_key_menubar.add_command(label = "[Delete] Delete the bloc whose header is located under the cursor")
    help_key_menubar.add_command(label = "[Space] to monitor the target variables in real time (on/off)")
    help_key_menubar.add_command(label = "[Escape] to close window")
    #-------------------------
    help_menubar.add_separator()
    #help_menubar.add_command(label = "Debug: Break point", command = break_point)
    #help_menubar.add_command(label = "Debug: Reset bloc", command = reset_blocs)
    #help_menubar.add_command(label = "Debug: calc. pos.", command = lambda: bloc.c_bloc_position(raz=False))
    #help_menubar.add_command(label = "Debug: RAZ pos.", command = lambda: bloc.c_bloc_position(raz=True))
    #help_menubar.add_separator()
    #help_menubar.add_command(label = "Debug: Reset draw", command = bloc.c_bloc_erase_draw)
    #help_menubar.add_command(label = "Debug: Redraw", command = bloc.c_bloc_redraw)
    #help_menubar.add_separator()
    doc_file = 'Documentation/Documentation_générale.html'
    if sys.platform == "linux":
        help_menubar.add_command(label = "Documentation", command = lambda: subprocess.Popen(['xdg-open', doc_file]))
    else:
        help_menubar.add_command(label = "Documentation", command = lambda: os.startfile(doc_file))
    help_menubar.add_separator()
    help_menubar.add_command(label = "Debug: print bloc", command = lambda: bloc.c_bloc_print())
    help_menubar.add_command(label = "Debug: print list_compiled", command = lambda: print_exeblocs())
    help_menubar.add_command(label = "Debug: print threads list", command = print_threads)
    help_menubar.add_command(label = "Debug: print connection status", command = print_connection)
    #help_menubar.add_separator()
    #help_menubar.add_command(label = "Debug: Compare", command = debug_compare)
    #help_menubar.add_command(label = "Debug: debug2", command = debug2)
    #-------------------------
    menubar.add_command(label = "   ")
    menubar.add_command(label = PARAM_ICONE_DISQUETTE, font=tkinter.font.Font(family="Helvetica", size=12), background = PARAM_COLOR_BG_HEADER_OUTPUT, command = lambda: save_file(save_as=False))
    menubar.add_command(label = " ")
    menubar.add_command(label = PARAM_ICONE_OEIL, font=tkinter.font.Font(family="Helvetica", size=14), background = PARAM_COLOR_BG_HEADER_OUTPUT, command = flip_monitoring)
    menubar.add_command(label = "   ")
    menubar.add_command(label = PARAM_ICONE_EVENT, font=tkinter.font.Font(family="Helvetica", size=14), background = PARAM_COLOR_BG_HEADER_OUTPUT, command = lambda: set_compile_thread("execute"))
def menu_target():
    global bloc, canvas, list_compiled, target_menubar, clientTCP
    if 'target_menubar' in globals():
        list_running = []
        proc_name = "menu_target: "
        for i in range(target_menubar.index(tkinter.END)):
            #print (proc_name, "  index=", 1, "  avant delete")
            target_menubar.delete(1)
            #print (proc_name, "  index=", 1, "  aprés delete")
        if clientTCP.socket == None:
            texteTCP = "Connect to Target"
            color_foreground = PARAM_COLOR_MENU_TEXTE_NORMAL
            color_activeforeground = PARAM_COLOR_MENU_TEXTE_NORMAL
        else:
            texteTCP = "Disconnect from Target"
            color_foreground = PARAM_COLOR_MENU_TEXTE_DANGER
            color_activeforeground = PARAM_COLOR_MENU_TEXTE_DANGER
        #print (proc_name, f"connection/disconnect: {clientTCP.socket}")
        target_menubar.add_command(label = texteTCP,  foreground = color_foreground, activeforeground = color_activeforeground, command = lambda: TCPconnect(clientTCP))
        #print (proc_name, "ajout Vérification")
        target_menubar.add_command(label = "Check <"+bloc.header['name']+">", command = lambda: set_compile_thread("verif"))
        if clientTCP.socket != None:
            #print (proc_name, "ajout Transfer")
            target_menubar.add_command(label = "Check & Transfer <"+bloc.header['name']+">", command = lambda: set_compile_thread("transfer"))
            #print (proc_name, "ajout Transfer & exécution")
            target_menubar.add_command(label = "Check, Transfer & Execute <"+bloc.header['name']+">", command = lambda: set_compile_thread("execute"))
def menu_header(event, elem):
    """construit le menu lié à un entête de bloc"""
    global menu_contextuel, list_threads
    proc_name = "menu_header: "
    print (proc_name, "elem=<{}>".format(elem))
    try:
        menu_contextuel.destroy()
    except:
        pass #print (proc_name, "pas de menu contextuel à destroy")
    menu_contextuel = Menu(master, tearoff=0)
    menu_contextuel.add_command(label = "Delete", foreground = PARAM_COLOR_MENU_TEXTE_DANGER, activeforeground = PARAM_COLOR_MENU_TEXTE_DANGER, command = lambda: del_bloc(elem))
    if True: #(elem.header['name'] != PARAM_NAME_BLOC_INPUT) and (elem.header['name'] != PARAM_NAME_BLOC_OUTPUT):
        menu_contextuel.add_command(label = "Update", command = lambda: update_bloc(elem))
    if not "system" in elem.header['key_word']:
        menu_contextuel.add_separator()
        menu_contextuel.add_command(label = "Open", command = lambda: open_bloc_new_window(elem.header['name'], elem.header['id'], (0,0)))
    print (proc_name, ":  elem.header['name']=", elem.header['name'])
    if elem.header['name'] == PARAM_NAME_BLOC_OUTPUT:
        print (proc_name, ":  output trouvé")
        menu_contextuel.add_separator()
        if 'event_id' in elem.header:
            prefix= "Change"
            sufix = ""
        else:
            prefix= "Add"
        menu_event = Menu(menu_contextuel)
        menu_contextuel.add_cascade(label = prefix+" event", menu = menu_event)
        if 'event_id' in elem.header:
            menu_event.add_command(label = "Delete event: ", foreground = PARAM_COLOR_MENU_TEXTE_DANGER, activeforeground = PARAM_COLOR_MENU_TEXTE_DANGER, command = lambda: del_event(elem))
        for i, thread in enumerate(list_threads):
            print (proc_name, ":  thread id=", thread['id'], "  thread period=", thread['period'])
            txt_index = "   " 
            if 'event_id' in elem.header:
                if elem.header['event_id']== thread['id']:
                     txt_index = PARAM_FLECHE_DROITE
            menu_event.add_command(label = txt_index+" "+thread['name'], command = capture_add_event(elem, thread['id']))
    if (elem.header['name'] == PARAM_NAME_BLOC_INPUT) or (elem.header['name'] == PARAM_NAME_BLOC_OUTPUT):
        menu_contextuel.add_separator()
        pos_io, nbr_io = io_interface_position(elem)
        menu_contextuel.add_command(label = "position:"+str(pos_io)+"/"+str(nbr_io))
        if pos_io > 1:
            menu_contextuel.add_command(label = "move up",   command = lambda: io_interface_move(elem, "up"))
        if pos_io < nbr_io:
            menu_contextuel.add_command(label = "move down", command = lambda: io_interface_move(elem, "down"))
    menu_contextuel.add_separator()
    doc_file = "Documentation/bloc_"+elem.header['name']+".html"
    if os.path.isfile(doc_file):
        if sys.platform == "linux":
            menu_contextuel.add_command(label = "Documentation", command = lambda: subprocess.Popen(['xdg-open', doc_file]))
        else:
            menu_contextuel.add_command(label = "Documentation", command = lambda: os.startfile(doc_file))
        menu_contextuel.add_separator()
    menu_contextuel.add_command(label = "Properties", command = lambda: properties_header(event.x_root, event.y_root, elem, modification=0))#0
    menu_contextuel.post(event.x_root, event.y_root)
def menu_io(event, io):
    """construit le menu lié à un IO"""
    global menu_contextuel
    proc_name = "menu_io: "
    #print (proc_name, "objet=<{}>".format(io))
    try:
        menu_contextuel.destroy()
    except:
        print (proc_name, "pas de menu contextuel à destroy")
    elem_parent = find_parent(io)

    menu_contextuel = Menu(master, tearoff=0)

    if 'lien' in io:
        menu_contextuel.add_command(label = "Delete link",  foreground = PARAM_COLOR_MENU_TEXTE_DANGER, activeforeground = PARAM_COLOR_MENU_TEXTE_DANGER, command = lambda: del_lien(io))
        menu_contextuel.add_separator()
    if not ("system" in elem_parent.header['key_word']):
        menu_contextuel.add_command(label = "Open", command = lambda: open_io_new_window(io))

    if (elem_parent.header['name'] == PARAM_NAME_BLOC_INPUT) or (elem_parent.header['name'] == PARAM_NAME_BLOC_OUTPUT): #rename
        #if (io['type'] == 'in') or (io['type'] == 'out'):
        menu_contextuel.add_command(label = "Rename", command = lambda: rename_io(event.x_root, event.y_root, io))

    try:
        io['local_name']
        menu_contextuel.add_command(label = "Change local name", command = lambda: change_local_name_io(event.x_root, event.y_root, io))
        menu_contextuel.add_command(label = "Delete local name", foreground = PARAM_COLOR_MENU_TEXTE_DANGER, activeforeground = PARAM_COLOR_MENU_TEXTE_DANGER, command = lambda: delete_local_name_io(event.x_root, event.y_root, io))
    except KeyError:
        if (elem_parent.header['name'] != PARAM_NAME_BLOC_OUTPUT and elem_parent.header['name'] != PARAM_NAME_BLOC_INPUT):
            if not 'system' in bloc.header['key_word']:
                menu_contextuel.add_command(label = "Create local name", command = lambda: change_local_name_io(event.x_root, event.y_root, io))

    if ((elem_parent.header['name'] == PARAM_NAME_BLOC_INPUT and bloc.header['name'] != PARAM_NAME_BLOC_OUTPUT) or \
        (elem_parent.header['name'] == PARAM_NAME_BLOC_OUTPUT and not 'system' in bloc.header) or \
        (io['type'] == 'in' and not 'system' in bloc.header)):
        menu_contextuel.add_command(label = "Set default value", command = lambda: set_defaut_value_io(event.x_root, event.y_root, io, "defaut_value"))


    #xxxif (elem_parent.header['name'] != PARAM_NAME_BLOC_OUTPUT):
    #xxx    if bloc.c_exesubloc_user_type ():
    #xxx        menu_contextuel.add_command(label = "Set default value", command = lambda: set_defaut_value_io(event.x_root, event.y_root, io, "defaut_value"))

    if (elem_parent.header['name'] == PARAM_NAME_BLOC_OUTPUT):
            if 'system' in bloc.header['key_word'] and bloc.header['name'] != PARAM_NAME_BLOC_INPUT:
                if "memory" not in io:
                    menu_contextuel.add_command(label = "Add Memory", command = lambda: memory_io("add", io))
                else:
                    menu_contextuel.add_command(label = "Delete Memory", command = lambda: memory_io("supp", io))


    if "memory" in io:
        if "initial_value" not in io:
            menu_contextuel.add_command(label = "Add initial value ", command = lambda: change_initial_value_io(event.x_root, event.y_root, io))
        else:
            menu_contextuel.add_command(label = "Change initial value ", command = lambda: change_initial_value_io(event.x_root, event.y_root, io))
            menu_contextuel.add_command(label = "Delete initial value ", command = lambda: delete_initial_value_io(event.x_root, event.y_root, io))


    menu_contextuel.add_separator()
    menu_contextuel.add_command(label = "OverWriting",  foreground = PARAM_COLOR_MENU_TEXTE_WARNING, activeforeground = PARAM_COLOR_MENU_TEXTE_WARNING, command = lambda: overwriting(io))
    menu_contextuel.add_separator()
    menu_contextuel.add_command(label = "Properties", command = lambda: properties_io(event.x_root, event.y_root, io))
    #menu_contextuel.add_command(label = "del defaut value", command = lambda: delete_defaut_value_io(event.x_root, event.y_root, io))
    #menu_contextuel.add_command(label = "del local defaut value", command = lambda: delete_local_defaut_value_io(event.x_root, event.y_root, io))
    menu_contextuel.post(event.x_root, event.y_root)
def open_file(pf_name, decal):
    """lit et dessine un bloc"""
    global canvas, mire, bloc, memo_bloc
    proc_name = "open_file: "
    #mire = c_mire(canvas)
    if pf_name==None:
        fname = filedialog.askopenfilename(initialdir= PARAM_CHEMIN_USER, title="Please select bloc", filetypes = [("Fichiers Bloc", "*.bloc")])
        print (proc_name, "file name=", fname)
        if not fname: return
    else:
        #fname = add_point_bloc_to_file_name(pf_name)
        fname = nom_complet_fichier(pf_name, False)
        print (proc_name, "ajout chemin et .bloc    file name=", fname)
    #print (proc_name, "fliename=", fname )
    if fname == None:
        print (proc_name, "fname=None", fname)
        return
    bloc.c_bloc_erase_draw()
    reset_blocs()
    bloc = read_bloc (fname)
    if bloc!=None:
        memo_bloc= bloc.c_bloc_copy()
        #print (proc_name, "bloc=", bloc)
        bloc.c_bloc_draw(master, canvas, mire)
        decalage = c_position(decal)
        print (proc_name, "avant décalage, decalage=", decal)
        canvas.move (ALL, scale_factor * decalage.x, scale_factor * decalage.y)
        routage()
        if not 'system' in bloc.header['key_word']:
            update_blocs()
    else:
        messagebox.showinfo("ERROR", "file reading error")
    menu_target()
    print (proc_name, "fin")
def save_file(save_as):
    """sauvegarde dun bloc en cours d'édition"""
    global bloc, memo_bloc
    proc_name = "save_file: "
    bloc_a_sauver = pickle.loads(pickle.dumps(bloc))
    if save_as:
        fullname = filedialog.asksaveasfilename(title="Please new bloc name", filetypes = [("Fichiers Bloc", "*.bloc")])
        print (proc_name, "file name=", fullname)
        if not fullname: return
        fname_sans_chemin = os.path.basename(fullname)
        fname_sans_extension = os.path.splitext(fname_sans_chemin)[0]
        bloc_a_sauver.header['name'] = fname_sans_extension
    print (proc_name, "début: name<"+bloc_a_sauver.header['name']+">")
    if bloc_a_sauver.header['structure_version']=="2.0":
        bloc.c_bloc_position(raz=True) #False
    else:
        print (proc_name, "Ce n'est pas une version 2.0")
    bloc_a_sauver.c_bloc_print()
    write_bloc (bloc_a_sauver)
    if not save_as:
        memo_bloc = bloc.c_bloc_copy()
    print (proc_name, "fin: name<"+bloc.header['name']+">")
    #print (proc_name, "fin")
def update_blocs():
    global bloc
    proc_name = "update_blocs: "
    print (proc_name, "début")
    print (proc_name, "calcule la position de tous les blocs")
    bloc.c_bloc_position(raz=False)
    update_error = False
    for i, elem in enumerate(bloc.sublocs):
        if (elem.header['name'] != PARAM_NAME_BLOC_INPUT):
            #print (proc_name, "updating bloc name=", elem.header['name'], "  id=", elem.header['id'])
            update_error = update_error or update_bloc(bloc.sublocs[i])
    if update_error:
        messagebox.showinfo("ERROR", "some sub-bloc can not be updated")
def reset_blocs():
    """supprimer tous les éléments (BLOC)"""
    global bloc
    proc_name = "reset_blocs: "
    #print (proc_name, "début")
    if 'bloc' in globals():
        del bloc
    else:
        print (proc_name, "il n'y pas de bloc à détruire")
    #print (proc_name, "fin")
def properties_header(px, py, elem, modification=0):
    """affiche les propriété du bloc édité et permet son édition"""
    def call_nul():
        return
    global bloc, list_threads
    proc_name = "proterties_header: "
    print (proc_name, "paramètre elem=", elem)
    if elem is bloc:
        #print (proc_name, "id(bloc.header)=", id(bloc.header))
        header = bloc.header
        proc_name         = elem.c_bloc_set_name
        proc_structure    = elem.c_bloc_set_structure
        proc_autor        = elem.c_bloc_set_autor
        proc_organisation = elem.c_bloc_set_organisation
        proc_key          = elem.c_bloc_set_key
        val_objet = bloc
        modification=True
    else:
        #print (proc_name, "id(elem.header)=", id(elem.header))
        header = elem.header
        proc_name         = call_nul
        proc_structure    = call_nul
        proc_autor        = call_nul
        proc_organisation = call_nul
        proc_key          = call_nul
        ###proc_event        = call_nul ###
        val_objet= elem
        modification=False
    pop = c_popup("bloc info", px+25, py+75)
    if val_objet is not bloc:
        pop.c_popup_add_une_propriete("id:", header['id'], call_nul)
    pop.c_popup_add_une_propriete("name:", header['name'], proc_name)
    pop.c_popup_add_une_propriete("structure version:", header['structure_version'], proc_structure)
    pop.c_popup_add_une_propriete("autor:", header['autor'], proc_autor)
    pop.c_popup_add_une_propriete("organisation:", header['organisation'], proc_organisation)
    for i, elem in enumerate(header['key_word']):
        pop.c_popup_add_une_propriete("Key"+str(i)+":", header['key_word'][i], proc_key)
    if val_objet is not bloc:
        pop.c_popup_add_une_propriete("index:", find_index_bloc(bloc, header['id']), call_nul)
    if header['name'] == PARAM_NAME_BLOC_OUTPUT:
        if 'event_id' in header:
            ith = find_thread_index(list_threads, header['event_id'])
            if ith == None:
                txt_event = "ID:"+header['event_id']+" not found"
            else:
                txt_event = list_threads[ith]['name']+"  "+str(list_threads[ith]['period'])+"(s)"
            pop.c_popup_add_une_propriete("event:", txt_event, call_nul) ###
    BP_escape = Button(pop.popup, text = 'Escape', width = 25, command = pop.popup.destroy)
    BP_escape.grid(row = pop.ligne, column = 0)
    if modification:
        BP_validation = Button(pop.popup, text='Validation', width = 25, command = lambda :pop.c_popup_validation(val_objet))
        BP_validation.grid(row = pop.ligne, column = 1)
    BP_escape.focus()
    BP_escape.bind("<Return>", lambda event: BP_escape.invoke())
    BP_escape.bind("<KP_Enter>", lambda event: BP_escape.invoke())
    BP_escape.bind("<Escape>", lambda event: BP_escape.invoke())

def print_exeblocs():
    global list_compiled
    proc_name = "print_exeblocs: "
    print (proc_name, "Liste des blocs compilés:   nb="+str(len(list_compiled)))
    for ebloc in list_compiled:
        print (proc_name, "   - EBLOC: name<"+ebloc.header['name']+">   /"+ebloc.header['AB'])
        print (ebloc)
def print_threads():
    global list_threads
    proc_name = "print_threads"
    print (proc_name, ":  liste des threads:")
    for ith, thread in enumerate(list_threads):
        print (proc_name, ":   - thread["+str(ith)+"] name="+thread['name']+"  période="+str(thread['period'])+"   compteur="+str(thread['counter']))
        for i, exe in enumerate(thread['list_exe']):
            print (proc_name, ":   - thread["+str(ith)+"]: list_exe["+str(i)+"]  execbloc name="+exe['exebloc'].header['name'])
            print (proc_name, ":   - thread["+str(ith)+"]: list_exe["+str(i)+"]   iesbloc="+str(exe['iesubloc']))
            print (proc_name, ":   - thread["+str(ith)+"]: list_exe["+str(i)+"]   run="+str(exe['run']))
def print_connection():
    proc_name = "print_connection"
    print (proc_name, f"clientTCP.socket={clientTCP.socket}")

def on_closing():
    """callback: sur evenement"""
    global master, bloc, memo_bloc, clientTCP, flag_monitoring, monitoring_thread
    def save_and_exit():
        save_file(new_name=False)
        master.destroy()
    proc_name = "on_closing: "
    print (proc_name, "début")
    if 'bloc' in globals() or bloc==None:
        if bloc.c_bloc_comp(memo_bloc):
            print (proc_name, "pas de modifs")
        else:
            print (proc_name, "il y a des modifs")
            popup = Toplevel(master)
            popup.wm_attributes("-topmost", True)
            popup.geometry("+{}+{}".format (int(config_window['pos_x']+50), int(config_window['pos_y']+50)))
            popup.title("Warnning")
            #popup.pack()
            Label(popup, text = "\r"+bloc.header['name']+".bloc   has changed!\r\rWould you like to save it?\r\r").pack()
            BP_no = Button(popup, text = 'no', width = 25, command = master.destroy)
            BP_yes = Button(popup, text = 'yes', width = 25, command = save_and_exit)
            BP_no.pack(side=LEFT)
            BP_yes.pack(side=RIGHT)
            BP_no.focus()
            BP_no.bind("<Return>", lambda event: BP_no.invoke())
            BP_no.bind("<KP_Enter>", lambda event: BP_no.invoke())
            BP_no.bind("<Escape>", lambda event: BP_no.invoke()) #
            BP_yes.bind("<Return>", lambda event: BP_yes.invoke())
            BP_yes.bind("<KP_Enter>", lambda event: BP_yes.invoke())
    if monitoring_thread != None:
        if monitoring_thread.is_alive():
            flag_monitoring = False
            time.sleep(0.3)
    clientTCP.close()            
    master.destroy()
def status_bar():
    #print ("status_bar: début")
    try:
        barre_de_status.pack_info()
    except:
        barre_de_status.pack(side = LEFT, fill=BOTH, expand=1)
    else:
        barre_de_status.pack_forget()
    #print ("status_bar: fin")
def break_point():
    print ("point d'arrêt")
def debug_compare():
    global bloc, memo_bloc
    proc_name = "debug_compare"
    print (proc_name, "<<<<comparaison>>>>>>")
    bloc.c_bloc_comp(memo_bloc)
def debug2():
    global bloc
    proc_name = "debug2"
    print (proc_name, "pas de code")

def TCPconnect(pclientTCP):
    proc_name = "TCPconnect: "
    print (proc_name, f"socket={pclientTCP.socket}")
    if pclientTCP.socket == None:
        print (proc_name, "cpclientTCP.connect")
        pclientTCP.connect()
        if pclientTCP.socket == None:
            messagebox.showinfo("ERROR",  f"Target (@IP:{PARAM_TCP_HOST_IP}) not reachable")
    else:
        print (proc_name, "pclientTCP.close")
        pclientTCP.close()
    menu_target()
    TCPstatus()
def TCPstatus():
    global clientTCP
    proc_name = "TCPstatus: "
    #print (proc_name, f"début:   socket={clientTCP.socket}")
    if clientTCP.socket == None:
        #print (proc_name, " socket=None")
        conn_status= "Disconnected" 
    else:
        #print (proc_name, " socket!=None")
        conn_status= "Connected"
    bar_connexion.config(text = "Target :"+conn_status)
def sendTCP(pcas):
    global clientTCP
    proc_name = "sendTCP: "
    print (proc_name, f"cas N°:{pcas}")
    clientTCP.send_message(pcas)
def set_running(pmonitoring_state):
    global bloc, canvas, config_window
    #global rt_menubar
    if pmonitoring_state:
        canvas.configure(bg = PARAM_COLOR_CANVAS_BG_MONITORING)
        bloc.c_bloc_show_title("Monitoring : ")
    else:
        canvas.configure(bg = config_window['canvas_bg_color'])
        bloc.c_bloc_show_title("editing : ")

def set_compile_thread(porder):
    global bloc
    proc_name = "set_compile_thread"
    print (proc_name, ": début")
    #menu_RT()
    bloc.c_bloc_show_title("Compiling: ")
    #running_event.set()
    compiling_thread = threading.Thread(target=compile_bloc, args=(bloc, porder))
    compiling_thread.start()
    #print (proc_name, ": fin")
def compile_bloc(pbloc, porder):
    """ Comfpilation du bloc et de ses sous-blocs """
    #global exeblocA, exeblocB
    global list_compiled, compile_level
    def edit_to_exe_blocs(pbloc, pexebloc, pparent_ids):
        """crée un bloc exécutables pour chaque bloc éditable (même les 'user')"""
        proc_name = "edit_to_exe_blocs: "
        for i, subloc in enumerate(pbloc.sublocs):
            print (proc_name, f" boucle1_creation_exe[{i}]: elem scruté: name<{subloc.header['name']}>  id={subloc.header['id']}")
            print (proc_name, f" boucle1_creation_exe[{i}]: création d'un subloc exécutable")
            pexebloc.sublocs.append(c_exesubloc(subloc, pparent_ids)) ######################################################### création dun sous-bloc exécutable
            esubloc = pexebloc.sublocs[-1]
            esubloc.header['counter'] = -1
            if not esubloc.c_exesubloc_user_type ():
                esubloc.header['procedure'] = recup_procedure(subloc)
            esubloc.inputs = recup_inputs(subloc)
            esubloc.outputs = recup_outputs(subloc)
            ajout_input_output(esubloc)
    def recup_inputs(psubloc):
        """ retourne les inputs """
        proc_name = "recup_inputs: "
        inputs = []
        for i, io in enumerate(psubloc.ios): #pour chaque IOS du subloc courant
            print (proc_name, f" ios 1er boucle: ois[{i}]  (io_name={io['name']},  io_type={io['type']},   id={io['id']})")
            if io['type']=='in':
                input = {}
                input['name'] = io['name']
                input['id'] = io['id']
                input['var'] = PARAM_VAL_INIT_INPUT
                input['valide'] = False
                if 'defaut_value' in io:
                    print (proc_name, f"   defaut_value trouvée,   valu={io['defaut_value']}")
                    input['defaut_value'] = input['var'] = io['defaut_value']
                    input['valide'] = True
                if 'local_name' in io:
                    print (proc_name, f"   local_name trouvée,   valu={io['local_name']}")
                    output['local_name'] = io['local_name']
                if 'lien' in io:
                    print (proc_name, "   lien trouvé,    lien={io['lien']}")
                    input['lien'] = io['lien']
                    input['valide'] = True
                inputs.append(input) #########
                #print (proc_name, " pour 'in'[", i,"]  aprés.append(input)     memio['ieo']=", memio['ieo'])
        print (proc_name, f"Retourne les inputs[]={inputs}")
        return inputs
    def recup_outputs(psubloc):
        """ retourne les outputs """
        proc_name = "recup_outputs: "
        outputs = []
        for i, io in enumerate(psubloc.ios): #pour chaque IOS du subloc courant
            print (proc_name, f" ios 1er boucle: ois[{i}]  (io_name={io['name']},  io_type={io['type']},   id={io['id']})")
            if io['type']=='out':
                output = {}
                output['name'] = io['name']
                output['id'] = io['id']
                if 'local_name' in io:
                    output['local_name'] = io['local_name']
                    #print (proc_name, "   il y a un <local_name>")
                output['var'] = PARAM_VAL_INIT_OUTPUT
                output['valide'] = False
                if 'defaut_value' in io:
                    print (proc_name, f"   defaut_value trouvée,   valu={io['defaut_value']}")
                    output['defaut_value'] = output['var'] = io['defaut_value']
                if 'local_name' in io:
                    print (proc_name, f"   local_name trouvée,   valu={io['local_name']}")
                    output['local_name'] = io['local_name']
                if 'memory' in io:
                    output['memory'] = io['memory']
                if 'initial_value' in io:
                    output['var'] = output['initial_value'] = io['initial_value']
                    output['valide'] = True
                outputs.append(output) #########
        print (proc_name, f"Retourne les output[]={outputs}")
        return outputs
    def ajout_input_output(pesubloc):
        """ pour les bloc INPUT  une entrée est générées (identique à la sortie existante)
            pour les bloc OUTPUT une sortie est générées (identique à l'entrée  existante)
            pour que les bloc INPUT et OUTPUT soient equivalents à un bloc de 'connection' """
        proc_name = "ajout_input_output"

        if pesubloc.header['name'] == PARAM_NAME_BLOC_INPUT:
            output = pesubloc.outputs[0]
            pesubloc.inputs.append(pickle.loads(pickle.dumps(output)))
            input = pesubloc.inputs[-1]
            input['id'] += 1
            input['var'] = PARAM_VAL_INIT_INPUT+1
            input['valide'] = True
            #if 'defaut_value' in ouput:
            #input['var'] = output['defaut_value']
            #input['valide'] = 

        if pesubloc.header['name'] == PARAM_NAME_BLOC_OUTPUT:
            input = pesubloc.inputs[0]
            pesubloc.outputs.append(pickle.loads(pickle.dumps(input)))
            output = pesubloc.outputs[-1]
            output['id'] += 1
            output['var'] = PARAM_VAL_INIT_OUTPUT+1
            output['valide'] = False
            if 'lien' in input:
                del pesubloc.outputs[-1]['lien']
    def find_index_of_lien (pexebloc, pparent_ids, plien):
        """ convert un lien (en id) en lien (en index executable)"""
        proc_name = "find_index_of_lien: "
        print (proc_name, f"parametres: parent_ids={pparent_ids}, lien={plien}")
        print (proc_name, f"parametres lien: parent={plien['id_parent']}, io={plien['id_io']}")
        for ib, elem in enumerate(pexebloc.sublocs):
            #print (proc_name, f"elem={elem}")
            if elem.parent_ids == pparent_ids:
                print (proc_name, f"parent_ids:  parameter={pparent_ids} == elem.parent_ids={elem.parent_ids}, ")
                if elem.header['id'] == plien['id_parent']:
                    print (proc_name, f"id:  parameter={plien['id_parent']} == elem.header['id']={elem.header['id']}, ")
                    for i, output in enumerate(elem.outputs):
                        print (proc_name, f"output: name={output}")
                        print (proc_name, f"output['id']'={output['id']}")
                        print (proc_name, f"plien['id_io']={plien['id_io']}")
                        if output['id']==plien['id_io']:
                            print (proc_name, f"return: bloc={ib}, output={i}")
                            return ib, i
        print (proc_name, f"ERREUR: lien non trouvé,   lien={plien}")
        return None
    def insert_user_sublocs(pexebloc):
        """ ajout les blocs constituant chaque USER"""
        global bloc
        ids = []
        proc_name = "insert_user_sublocs"
        for i, esubloc in enumerate(pexebloc.sublocs):
            print (proc_name, f" boucle_blocs[{i}]: elem scruté: name<{esubloc.header['name']}>  id={esubloc.header['id']}")
            if esubloc.c_exesubloc_user_type ():
                print (proc_name, f" boucle_bocle[{i}]: USER bloc trouvé: name<{esubloc.header['name']}>  id={esubloc.header['id']}")
                if not 'compiled' in esubloc.header:
                    print (proc_name, f" boucle_blocs{i}]: bloc non complié name<{esubloc.header['name']}>  id={esubloc.header['id']},  key_word={esubloc.header['key_word']}")
                    ids = pickle.loads(pickle.dumps(esubloc.parent_ids))
                    ids.append(esubloc.header['id'])
                    user_bloc = read_bloc (nom_complet_fichier(name=esubloc.header['name'], psystem=False))############# lecture USER bloc
                    user_bloc.c_bloc_delete_event ()
                    esubloc.header['compiled'] = True
                    edit_to_exe_blocs(user_bloc, pexebloc, ids)
                    faire_liens(pexebloc, ids)
                else: 
                    print (proc_name, f" boucle_blocs{i}]: bloc déjà complié name<{esubloc.header['name']}>  id={esubloc.header['id']},  key_word={esubloc.header['key_word']},   compiled={esubloc.header['user_compiled']}")
    def faire_liens(pexebloc, pids):
        """ transforme les liens d'id en index (intra USER ou niveau racine)"""
        proc_name = "faire_liens: "
        for i, esubloc in enumerate(pexebloc.sublocs):
            print (proc_name, f" boucle_lien[{i}]: elem scruté: name<{esubloc.header['name']}>  id={esubloc.header['id']}")
            if not esubloc.c_exesubloc_user_type ():
                for j, input in enumerate(esubloc.inputs):
                    if 'lien' in input:
                        print (proc_name, f"boucle_inputs[{j}]  (name<{input['name']}>,  id={input['id']},   lien={input['lien']})")
                        #input['lien_bloc_index'], input['lien_output_index'] = find_index_of_lien(pexebloc, pids, input['lien'])
                        bloc_index, output_index = find_index_of_lien(pexebloc, esubloc.parent_ids, input['lien'])
                        if bloc_index != -1 and output_index != -1:
                            if not pexebloc.sublocs[bloc_index].c_exesubloc_user_type ():
                                input['lien_bloc_index'] = bloc_index
                                input['lien_output_index'] = output_index 
                                del(input['lien'])
                            else:
                                print (proc_name, f"boucle_inputs[{j}] PAS de suppression du 'lien' (name<{input['name']}>,  id={input['id']},   lien={input['lien']})  parceque la cible est un USER")
                    else:
                        print (proc_name, f"boucle_inputs[{j}]  (name<{input['name']}>,  id={input['id']},   PAS de lien)")
            else:
                print (proc_name, f"<{esubloc.header['name']}>,  id={esubloc.header['id']} est un bloc USER donc on ne refait pas les liens")

    def find_index_of_input_bloc_of_bloc_input (pexebloc, puser_bloc_index, puser_input_id):
        """ returne l'index du bloc "INPUT" correspondant à une patte d'entrée dun USER"""
        user_sublocs_ids = []
        proc_name = "find_index_of_input_bloc_of_bloc_input : "
        user_bloc = pexebloc.sublocs[puser_bloc_index]
        print (proc_name, f"USER bloc:  (name<{user_bloc.header['name']}>,  id={user_bloc.header['id']}")
        print(proc_name, f"user_bloc_ids={user_bloc.parent_ids}")
        user_sublocs_ids = pickle.loads(pickle.dumps(user_bloc.parent_ids))
        user_sublocs_ids.append(user_bloc.header['id'])
        print(proc_name, f"user_bloc.parent_id={user_bloc.parent_ids}")
        print(proc_name, f"user_sublocs_ids={user_sublocs_ids}")
        print(proc_name, f"user_bloc.parent_id={user_bloc.parent_ids}")
        find = False
        for i, esubloc in enumerate(pexebloc.sublocs):
            print (proc_name, f" boucle_bloc i[{i}]: bloc scruté: name<{esubloc.header['name']}>  id={esubloc.header['id']}")
            if esubloc.parent_ids == user_sublocs_ids:
                print (proc_name, f" boucle_bloc i[{i}]: ids==ids: name<{esubloc.header['name']}>  id={esubloc.header['id']},   ids={esubloc.parent_ids}")
                if esubloc.header['id'] == puser_input_id:
                    print (proc_name, f" boucle_bloc i[{i}] ____trouvé___(id==id)_: retourne le bloc (name<{esubloc.header['name']}>  id={esubloc.header['id']})")
                    return i
        if not find:
            Print (proc_name, f"ERROR: INPUT bloc of USER bloc input not found")
    def find_index_of_output_bloc_of_user_bloc_output(pexebloc, puser_bloc_index, puser_output_id):
        """ retourne l'indexe du bloc "OUTPUT" correspondant à une patte de sortie dun USER"""
        user_sublocs_ids = []
        proc_name = "find_output_bloc_of_user_bloc_output: "
        user_bloc = pexebloc.sublocs[puser_bloc_index]

        print (proc_name, f"USER bloc:  (name<{user_bloc.header['name']}>,  id={user_bloc.header['id']}")
        print(proc_name, f"user_bloc_ids={user_bloc.parent_ids}")
        user_sublocs_ids = pickle.loads(pickle.dumps(user_bloc.parent_ids))
        user_sublocs_ids.append(user_bloc.header['id'])
        print(proc_name, f"user_bloc.parent_id={user_bloc.parent_ids}")
        print(proc_name, f"user_sublocs_ids={user_sublocs_ids}")
        print(proc_name, f"user_bloc.parent_id={user_bloc.parent_ids}")
        find = False
        for i, esubloc in enumerate(pexebloc.sublocs):
            print (proc_name, f" boucle_bloc i[{i}]: bloc scruté: name<{esubloc.header['name']}>  id={esubloc.header['id']}")
            if esubloc.parent_ids == user_sublocs_ids:
                print (proc_name, f" boucle_bloc i[{i}] ids==ids: name<{esubloc.header['name']}>  id={esubloc.header['id']},   ids={esubloc.parent_ids}")
                if esubloc.header['id'] == puser_output_id:
                    print (proc_name, f" boucle_bloc i[{i}] ____trouvé___(id==id)_: retourne le bloc (name<{esubloc.header['name']}>  id={esubloc.header['id']})")
                    return i
        if not find:
            print (proc_name, f"ERROR: OUTPUT bloc of USER bloc output not found")

    def faire_lien_user_input(pexebloc):
        proc_name = "faire_lien_user_input"
        for i, esubloc in enumerate(pexebloc.sublocs):
            print (proc_name, f" boucle_bloc i[{i}]: bloc scruté: name<{esubloc.header['name']}>  id={esubloc.header['id']}")
            if esubloc.c_exesubloc_user_type ():
                user_bloc = esubloc
                print (proc_name, f" bloc_bloc i[{i}]:  USER bloc trouvé:  name<{user_bloc.header['name']}>  id={user_bloc.header['id']},   ids={user_bloc.parent_ids}")
                for j, user_bloc_input in enumerate(user_bloc.inputs):
                    find = False
                    print (proc_name, f" boucle_input j[{j}]: input scruté: name<{user_bloc_input['name']}>  id={user_bloc_input['id']}")
                    index_input_bloc = find_index_of_input_bloc_of_bloc_input (pexebloc, i, user_bloc_input['id'])
                    input_bloc = pexebloc.sublocs[index_input_bloc]
                    print (proc_name, f" boucle_input j[{j}]: INPUT bloc of USER trouvé:  name<{input_bloc.header['name']}>  id={input_bloc.header['id']}")
                    if 'lien' in user_bloc_input:
                        print (proc_name, f" boucle_input j[{j}] un lien trouvé dans l'input (name<{user_bloc_input['name']}>,  id={user_bloc_input['id']})   lien={user_bloc_input['lien']}")
                        index_bloc, index_output = find_index_of_lien(pexebloc, user_bloc.parent_ids, user_bloc_input['lien'])
                        if pexebloc.sublocs[index_bloc].c_exesubloc_user_type():    # si enchainement de USER bloc
                            print (proc_name, f"((((((((((enchainement de USER)))))))))))))))))))))))))))")
                            output_id = pexebloc.sublocs[index_bloc].outputs[index_output]['id']
                            index_previous_user_output_bloc = find_index_of_output_bloc_of_user_bloc_output(pexebloc, index_bloc, output_id)
                            input_bloc.inputs[0]['lien_bloc_index']   = index_previous_user_output_bloc
                            input_bloc.inputs[0]['lien_output_index'] = 0
                            user_bloc_input['monitoring_type'] = "out"
                            user_bloc_input['monitoring_bloc_index'] = index_input_bloc
                            user_bloc_input['monitoring_io_index'] =  0
                        else:   # si le USER pointe vers un bloc SYSTEM
                            input_bloc.inputs[0]['lien_bloc_index']   = index_bloc
                            input_bloc.inputs[0]['lien_output_index'] = index_output
                            user_bloc_input['monitoring_type'] = "out"
                            user_bloc_input['monitoring_bloc_index'] = index_input_bloc
                            user_bloc_input['monitoring_io_index'] =  0
                    else:
                        if 'defaut_value' in user_bloc_input:
                            print (proc_name, f"   defaut_value trouvée, dans USER input: defaut value={user_bloc_input['defaut_value']}")
                            input_bloc.inputs[0]['defaut_value'] = user_bloc_input['defaut_value']
                            input_bloc.inputs[0]['valide'] = True 
                        else:
                            print (proc_name, f"ERROR: USER bloc input do not have link or defaut_value")
                    if not find:
                        print (proc_name, f"ERROR???:  USER bloc")
                                     
        print(proc_name, "fin")
    def faire_lien_user_output(pexebloc):
        proc_name = "faire_lien_user_output"
        for i, esubloc in enumerate(pexebloc.sublocs):
            print (proc_name, f" boucle_bloc i[{i}]: bloc scruté: name<{esubloc.header['name']}>  id={esubloc.header['id']}")
            if esubloc.c_exesubloc_user_type ():
                user_bloc = esubloc
                print (proc_name, f" boucle_bloc i[{i}]: USER bloc trouvé:  (name<{user_bloc.header['name']}>,  id={user_bloc.header['id']},  ids={user_bloc.parent_ids})")
                for j, user_bloc_output in enumerate(esubloc.outputs):
                    find = False
                    print (proc_name, f" boucle_output j[{j}]: output scrutée (name<{user_bloc_output['name']}>,  id={user_bloc_output['id']})")
                    index_output_bloc = find_index_of_output_bloc_of_user_bloc_output(pexebloc, i, user_bloc_output['id'])
                    output_bloc = pexebloc.sublocs[index_output_bloc]
                    print (proc_name, f" boucle_output j[{j}]: OUTPUT bloc of USER trouvé:  name<{output_bloc.header['name']}>  id={output_bloc.header['id']}")
                    for ii, esubloc2 in enumerate(pexebloc.sublocs):
                        print (proc_name, f" boucle_bloc ii[{ii}] bloc scruté: name<{esubloc2.header['name']}>  id={esubloc2.header['id']}")
                        if esubloc2.parent_ids == esubloc.parent_ids:
                            print (proc_name, f" boucle_bloc ii[{ii}] ids==ids:    {esubloc2.parent_ids}=={esubloc.parent_ids}")
 
                            for jj, input in enumerate(esubloc2.inputs):
                                print (proc_name, f" boucle_input jj[{jj}] input scruté (name<{input['name']}>,  id={input['id']}")
                                if 'lien' in input:
                                    print (proc_name, f" boucle_input jj[{jj}] input avec lien (name<{input['name']}>,  id={input['id']})  lien={input['lien']}")                                   
                                    if input['lien']['id_parent'] == esubloc.header['id'] and input['lien']['id_io'] == user_bloc_output['id']:
                                        print (proc_name, f" boucle_input jj[{jj}] bloc ver la patte output du USER Trouvé; bloc (name<{esubloc2.header['name']}>, id={esubloc2.header['id']},  input (name<{input['name']}>, id={input['id']}")
                                        input['lien_bloc_index'] = index_output_bloc
                                        input['lien_output_index'] = 0
                                        user_bloc_output['monitoring_type'] = "out"
                                        user_bloc_output['monitoring_bloc_index'] = index_output_bloc
                                        user_bloc_output['monitoring_io_index'] =  0
                    if not find:
                        print (proc_name, f"ERROR: aucun bloc ne pointe vers ce USER bloc")
        print(proc_name, "fin")

    def monitoring_user_liensxxx (pexebloc):
        """ cré des liens pour le monitonring des io des bloc USER """
        proc_name = "monitoring_user_liens: "
        for i, esubloc in enumerate(pexebloc.sublocs):
            print (proc_name, f" 1) boucle_lien[{i}]: elem scruté: name<{esubloc.header['name']}>  id={esubloc.header['id']}")
            if esubloc.c_exesubloc_user_type ():
                print (proc_name, f" 1) boucle_lien[{i}]: c'est un bloc USER: name<{esubloc.header['name']}>  id={esubloc.header['id']}")
                for j, input in enumerate(esubloc.inputs):
                    print (proc_name, f"boucle_inputs[{j}]  (name<{input['name']}>,  id={input['id']})")
                    if 'lien' in input:
                        print (proc_name, f"boucle_inputs[{j}]  (name<{input['name']}>,  id={input['id']},   lien={input['lien']})")
                        input['monitoring_type'] = "out"
                        input['monitoring_bloc_index'], input['monitoring_io_index'] = find_index_of_lien(pexebloc, esubloc.parent_ids, input['lien']) 
                    else:
                        print (proc_name, f"boucle_inputs[{j}]  (name<{input['name']}>,  id={input['id']},   PAS de lien)")
                for k, output in enumerate(esubloc.outputs):
                    print (proc_name, f"boucle_outputs[{k}]  (name<{output['name']}>,  id={output['id']})")
                    for ii, esubloc2 in enumerate(pexebloc.sublocs):
                        print (proc_name, f" boucle_recherche bloc scruté:   esubloc2[{ii}]: elem scruté: name<{esubloc2.header['name']}>  id={esubloc2.header['id']}")
                        for jj, input2 in enumerate(esubloc2.inputs):
                            if 'lien' in input2:
                                print (proc_name, f"boucle_inputs2[{jj}] lien trouvé (name<{input2['name']}>,  id={input2['id']},   lien={input2['lien']})")
                                if esubloc.header['id'] == input2['lien']['id_parent'] and output['id'] == input2['lien']['id_io']:
                                    print (proc_name, f"boucle_inputs2[{jj}] pointe (name<{input2['name']}>,  id={input2['id']},   lien={input2['lien']})")
                                    if esubloc.parent_ids == esubloc2.parent_ids:
                                        print(proc_name, f"TROUVé affectation monitoring,  bloc{ii},  output{jj}")
                                        output['monitoring_type'] = "in"
                                        output['monitoring_bloc_index'] = ii
                                        output['monitoring_io_index']   = jj

    global compile_level
    proc_name = "compile_bloc: "
    print (proc_name, "------------------------------------------------début - BLOC éditabel")
    bloc.c_bloc_print()
    print (proc_name, "--------------------------------------------------------Bloc éditable - fin")
    print(proc_name, "\n\n____________________________________________________________début de compilation des blocs___________________________________________________________________")
    compile_level =0
    error_compil = None
    print (proc_name, f", début de compilation du bloc: name<"+pbloc.header['name']+">  order="+porder)
    racine_ids = [0] # le premier niveau n'a pas de parent (soit 0)
    print (proc_name, f"racine_ids={racine_ids}")
    exebloc = c_exebloc(pbloc) ################################################ création du bloc executable principal (seulement l'entête)

    print(proc_name, "__(étape 1)________________________________________________N0____crée un bloc exécutables pour chaque bloc éditable (même les 'user')")
    edit_to_exe_blocs(pbloc, exebloc, racine_ids)
    print(proc_name, "____________________________N0_____convertit les liens d'id en index")
    faire_liens(exebloc, racine_ids)

    print (proc_name, f"\n\n___EXEBLOC: name<{exebloc.header['name']}>______________________PRINT: exebloc avec tous les blocs du niveau 0 et liens 'index'\n", exebloc)

    print(proc_name, "__(étape 2)________________________________________________N0/1_____insertion des blocs des USERs N0")
    insert_user_sublocs(exebloc)


    print (proc_name, f"\n\n___EXEBLOC: name<{exebloc.header['name']}>______________________PRINT: exebloc avec USER et lien index intra USER\n", exebloc)

    faire_lien_user_output(exebloc)
    faire_lien_user_input(exebloc)
    print (proc_name, f"\n\n___EXEBLOC: name<{exebloc.header['name']}>______________________PRINT: exebloc avec USER, lien index intra USER, INPUT et OUTPUT\n", exebloc)

    
    for i in range(0,100):
        print (proc_name, f"boucle de compilation: i=[{i}]")
        all_user_bloc_compiled = True
        all_user_bloc_compiled1 = True
        for esubloc in exebloc.sublocs:
            if esubloc.c_exesubloc_user_type ():
                if 'compiled' in esubloc.header:
                    pass 
                else:
                    all_user_bloc_compiled = False

            all_user_bloc_compiled1 = all_user_bloc_compiled1 and ('compiled' in esubloc.header or not esubloc.c_exesubloc_user_type ())
        print (proc_name, f"all_user_bloc_compiled ={all_user_bloc_compiled}")    
        print (proc_name, f"all_user_bloc_compiled&={all_user_bloc_compiled1}")    
        if all_user_bloc_compiled:
            print (proc_name, f"boucle de compilation: BREAK: avant execution, i=[{i}]")
            break


        print(proc_name, "__(étape 3)________________________________________________N1/2_____insertion des blocs des USERs N1")
        insert_user_sublocs(exebloc)


        print (proc_name, f"\n\n___EXEBLOC: name<{exebloc.header['name']}>___________N1/2_______PRINT: exebloc avec USER N0 et N1 et lien index intra USER\n", exebloc)

        faire_lien_user_output(exebloc)
        faire_lien_user_input(exebloc)
        print (proc_name, f"\n\n___EXEBLOC: name<{exebloc.header['name']}>___________N1/2_______PRINT: exebloc avec USER N0 et N1, lien index intra USER et INPUT et OUTPUT\n", exebloc)
    #---fin de compilation des blocs--------------------------------

    print (proc_name, "------------------------------------------------début - BLOC éditabel")
    bloc.c_bloc_print()
    print (proc_name, "--------------------------------------------------------Bloc éditable - fin")

    if len(list_compiled) > 0:
        del list_compiled[-1]
    list_compiled.append(exebloc) # utilisé par l'onglet DEBUG

    exebloc.header['building'] = datetime.now()

    #____________________________________________erreur ou vérif
    if error_compil != None or porder == "verif":
        if error_compil != None:
            txt_compil = " ERROR: Checking aborted (code="+str(error_compil)+")\nthe bloc <"+pbloc.header['name']+"> is invalide"
        else:
            txt_compil = "The bloc <"+pbloc.header['name']+"> is valide"
        print (proc_name, txt_compil)
        messagebox.showinfo("Compilation Status:", txt_compil)
    #______________________________________________________________________________________________________pas d'erreur et (transfer ou execute)
    if error_compil == None and (porder == "transfer" or porder == "execute") and clientTCP.socket != None:
        if porder == "execute": txt_execute = "\n and execute?"
        else: txt_execute = ""
        reponse = messagebox.askquestion("Confirmation", "The bloc <"+pbloc.header['name']+"> is valide\nSend it to the target?"+txt_execute)
        if reponse == 'yes':
            print(proc_name, "L'utilisateur a choisi Oui")
            exebloc_dump = pickle.dumps(exebloc)
            #exebloc_str = pickle.dumps(exebloc).decode('utf-8')
            #print(trace_txt, "   str(exebloc_str):", str(exebloc_str))
            #print(trace_txt, "   exebloc_str:", exebloc_str)
            clientTCP.send_message(porder.encode('utf-8')+b":"+exebloc_dump)
        else:
            print(proc_name, "L'utilisateur a choisi Non")
    menu_target()
    print (proc_name,"_____________________________________fin de compilation")
def monitoring_bloc():
    """ thread: Visualisation en temps réel d'un bloc ou sous-blocs """
    global master, canvas, fag_monitoring
    def bg_color(valide):
        """ retourne la couleur du fond selon la validité"""
        if valide: 
            return PARAM_COLOR_BG_IO_TRUE 
        else:
            return PARAM_COLOR_BG_IO_FALSE 
    def formatage(var):
        """ retourne la valeur mais formatée"""
        if isinstance(var, float):
            return f"{var:8.3f}"
        else:
            return var
    def show_io(ptype, pio, pmsb, pid):
        proc_name = "show_io: "
        #print (proc_name, f"parametres: type={ptype},   io(name={pio['name']}, type={pio['type']}, id={pio['id']}),  msb_name={pmsb.header['name']}, id={pid}")
        if ptype == 'in':
            for minput in pmsb.inputs:
                if minput['id'] == pid:
                    canvas.itemconfig(io['id_cadre'], fill=bg_color(minput['valide']))
                    canvas.itemconfig(io['id_texte'], text=formatage(minput['var']))
        elif ptype == 'out':
            for moutput in pmsb.outputs:
                if moutput['id'] == pid:
                    canvas.itemconfig(io['id_cadre'], fill=bg_color(moutput['valide']))
                    canvas.itemconfig(io['id_texte'], text=formatage(moutput['var']))
        else:
            messagebox.showinfo("ERROR", f"Shoing IO 'type' is not 'in' or 'out',  io={pio}")


    monitoring = {}
    arbo_ids = []
    proc_name = "monitoring_bloc: "
    #print(proc_name, "début")
    #print(proc_name, "décodage arborescence du nom du bloc à monitorer")
    lignée=master.title()
    list_blocs = lignée.split("/")
    #print(proc_name, f" list={list_blocs}")
    list_blocs.pop(0)
    #print(proc_name, f" list={list_blocs}")
    mssg = ""
    for i, blc in enumerate(list_blocs):
        if i==0:
            monitoring['name'] = blc
            arbo_ids.append(0)
        else:
            ip = blc.find(")")
            arbo_ids.append(int(blc[1:ip]))
    monitoring['arbo_ids'] = arbo_ids
    #print(proc_name, f"  monitoring['name']={monitoring['name']}")
    #print(proc_name, f"  monitoring['arbo_ids']={monitoring['arbo_ids']}")
    msg_dump = pickle.dumps(monitoring)
    #print (proc_name, "   msg_dump:", msg_dump)
    message=b"monitoring:"+msg_dump
    #print (proc_name, "   message envoyé à la cible:", message)
    while flag_monitoring:
        if True: #try:
            clientTCP.send_message(message)
            buff = clientTCP.receive_message()
            if buff == b"monitoring:not_found":
                messagebox.showinfo("ERROR", f"Monitoring not allowed, because the target does not contain bloc <{monitoring['name']}>")
                flip_monitoring()
                break
            else:
                monitored_sublocs = pickle.loads(buff)
                for i, sb in enumerate(bloc.sublocs):
                    #print(proc_name, f" monitoring bloc=<{monitoring['name']}>, monitored_subloc[{i}].header['name']=<{msb.header['name']}>")
                    for j, io in enumerate(sb.ios):
                        #print(proc_name, f" : ois[{k}]['name']=<{io['name']}> ios[{j}]['id']=<{io['id']}> ios[{j}].['id_texte']=<{io['id_texte']}>")
                        for ii, msb in enumerate(monitored_sublocs):
                            if msb.header['id'] == sb.header['id']:
                                #print(proc_name, f"bloc SYSTEM id==id: monitored_subloc[{ii}].header['name']=<{msb.header['name']}> bloc.subloc[{j}].header['name']=<{sb.header['name']}>")
                                show_io (io['type'], io, msb, io['id'])

            time.sleep(0.1)
        else: #except:
            print(proc_name, "EXECPTION: buffer reçu=", buff)
    bloc.c_bloc_redraw()
    print(proc_name, "fin")


#  début --- début --- début --- début --- début --- début --- début --- début --- début --- début --- début --- début --- début --- début ---
proc_name = "__main__: "
if __name__ == '__main__':
    print (proc_name, "début du main:")
    print (proc_name, "sys.argg: <", sys.argv, ">")
    print (proc_name, "nb arg=<", len(sys.argv), ">")
# index des arguments
PARAM_ARG_CODE_PYTHON = 0
PARAM_ARG_DECAL_WINDOW_X = 1
PARAM_ARG_DECAL_WINDOW_Y = 2
PARAM_ARG_BLOC_NAME = 3
PARAM_ARG_MONITORING = 4
PARAM_ARG_DECAL_X = 5
PARAM_ARG_DECAL_Y = 6
PARAM_ARG_ARBORESCENCE = 7
PARAM_ARG_NBR_MAIN = 1
PARAM_ARG_NBR_SECOND = 3

config_window={}
master = Tk()
master.resizable(True, True)
config_window['largeur']= int (master.winfo_screenwidth()//PARAM_RATIO_FENETRE_A_LOUVERTURE)
config_window['hauteur']= int (master.winfo_screenheight()//PARAM_RATIO_FENETRE_A_LOUVERTURE)
flag_monitoring = False
print (proc_name, f"nb arg={len(sys.argv)}")
for i,arg in enumerate(sys.argv):
    print (proc_name, f" dans boucle, argument[{i}]={sys.argv[i]}")
    if (i==PARAM_ARG_MONITORING and arg==PARAM_MODE_MONITORING):  # décalage de la nouvelle fenêtre
        flag_monitoring = True
print (proc_name, "flag_monitoring=<", flag_monitoring, ">")
if len(sys.argv) > PARAM_ARG_NBR_MAIN:
    print (proc_name, "décalage de la fenêtre")
    config_window['pos_x']= int(sys.argv[PARAM_ARG_DECAL_WINDOW_X]) +50
    config_window['pos_y']= int(sys.argv[PARAM_ARG_DECAL_WINDOW_Y]) +50
else:
    print (proc_name, "pas de décalage de la fenêtre")
    config_window['pos_x']= (master.winfo_screenwidth()-config_window['largeur'])//2
    config_window['pos_y']= (master.winfo_screenheight()-config_window['hauteur'])//2
if len(sys.argv) > PARAM_ARG_NBR_SECOND:
    config_window['canvas_bg_color'] = PARAM_COLOR_CANVAS_BG_SECOND 
else:
    config_window['canvas_bg_color'] = PARAM_COLOR_CANVAS_BG_MAIN
txt_geometry =f"{config_window['largeur']}x{config_window['hauteur']}+{config_window['pos_x']}+{config_window['pos_y']}"
print (proc_name, f"config. window: {txt_geometry}")
master.geometry (txt_geometry)
master.config(bd=5, relief="groove")
master.update()
scale_factor = 1.

# création du canevas
canvas = Canvas(master, bg=config_window['canvas_bg_color'])
canvas.pack(fill='both', expand=True, padx = 0, pady = 0)

# création de la barre de status
barre_de_status = Frame(master)
bar_connexion = Label(barre_de_status, text="Target : Disconnected") 
bar_souris_canv = Label(barre_de_status, text="position souris dans repère canvas") #, bg="orange"
bar_coeff_zoom= Label(barre_de_status, text="coeff zoom")
bar_souris_mire = Label(barre_de_status, text="position souris dans repère Mire")
barre_de_status.pack(side = LEFT, fill=BOTH, expand=1)
bar_connexion.pack(side =LEFT, expand=1)
bar_souris_canv.pack(side =LEFT, expand=1)
bar_coeff_zoom.pack(side = LEFT, expand=1)
bar_souris_mire.pack(side = RIGHT, expand=1)
master.update()
master.resizable(width=True, height=True)

# dessine la mire en 0,0
mire= c_mire(canvas)
zoom(PARAM_ZOOM_DEFAUT, canvas.winfo_width() // 2, canvas.winfo_height() // 2)         # applique le zoom par défaut

bloc = c_bloc (master)
memo_bloc = bloc.c_bloc_copy()
bloc.c_bloc_show_title("editing: ")

# callback
canvas.bind("<Button-1>", event_clic_gauche)
canvas.bind("<ButtonRelease-1>", event_release_gauche)
canvas.bind("<Button-2>", event_clic_molette)
canvas.bind("<Button-3>", event_clic_droit)
canvas.bind("<B2-Motion>", event_deplacement_molette_enfonce)
#canvas.bind("<Button-4>", event_molette_poussee)
#canvas.bind("<Button-5>", event_molette_tiree)
if sys.platform == "linux":
    canvas.bind("<Button-4>", event_molette)
    canvas.bind("<Button-5>", event_molette)
else:
    canvas.bind("<MouseWheel>", event_molette)
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
canvas.bind("<Motion>", event_deplacement_souris)
master.bind("<KeyPress-space>", event_key_space)
master.bind("<Escape>", event_key_escape)
master.bind("<KeyPress-F1>", event_key_F1)
master.bind("<KeyPress-F3>", event_key_F3)
master.bind("<KeyPress-F4>", event_key_F4)
master.bind("<KeyPress-F5>", event_key_F5)
master.bind("<KeyPress-F7>", event_key_F7)
master.bind("<KeyPress-Delete>", event_key_delete)

master.protocol("WM_DELETE_WINDOW", on_closing)

clientTCP = TCPClient()
TCPconnect(clientTCP) # connexion automatique

# création du menu static
menu_bar()


# Création des évènements périodiques (arment du motor d'exécution)
#for i, thread in enumerate(list_threads):
#    #print ("création du running threads N°",i, "thread=", thread)
#    periodic (thread)

if len(sys.argv) > PARAM_ARG_NBR_SECOND:
    name = sys.argv[PARAM_ARG_BLOC_NAME]
    print (proc_name, "bloc: name=<", name, ">")

    decalage = [float(sys.argv[PARAM_ARG_DECAL_X]), float(sys.argv[PARAM_ARG_DECAL_Y])]
    print (proc_name, "decalage=", decalage)
    #if flag_monitoring: arborescence = sys.argv[PARAM_ARG_ARBORESCENCE]
    arborescence = sys.argv[PARAM_ARG_ARBORESCENCE]
    if name=="": name=None
    open_file (name, decalage) #___ouverture du bloc passé en paramètre
    if flag_monitoring:
        flag_monitoring = not flag_monitoring
        flip_monitoring()


#run_clientTCP()
# Exemple d'utilisation

    #clientTCP = TCPClient()
    #clientTCP.connect()
    # Pause de 3.5 secondes
    #time.sleep(0.2)
    #clientTCP.send_message("Hello, server!")
    #response = clientTCP.receive_message()
    #print(f"Réponse0 du serveur : {response}")
    #response = clientTCP.receive_message()
    #print(f"Réponse1 du serveur : {response}")
    #clientTCP.close()
master.mainloop()

