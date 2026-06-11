#!/bin/bash
source ../../venv/bin/activate
python3 main.py








##To launch the "Blocaine" interpreter on the target, you have two options:
##CHOICE 1: The simplest option is to launch the "Blocaine" interpreter using the following basic command: python3 main.py. In this case, you cannot specify the priority of the Python interpreter, and you cannot use the standard port dedicated to the HTTP protocol (port 80) for the Blocaine web server; therefore, the port defined in `PARAM_NETWORK.py` file will be used (defaut value is 8080)
##CHOICE 2: Launch the "Blocaine" interpreter using the following "super user" command: sudo nice -n -12 python3 main.py`. In this case, the priority of the Python interpreter is increased (`nice -n -12`) and you have the option to use port 80 for the Blocaine web server (by first setting `PARAM_HTTP_PORT = 80` in the `PARAM_NETWORK.py` file), but you must enter your "sudo" password.
##remenber:
    ##The HTTP port of the Blocaine web server is defined by the PARAM_HTTP_PORT parameter in the PARAM_NETWORK.py file; its default value is 8080.
    ##You need to use "sudo" to launch Python interpreter, if you want to use the standard HTTP port 80 for Blocaine web server

# Commande à lancer SI le mot de passe sudo est valide
#COMMANDE_SUDO="sudo nice -n -12 python3 main.py"

# Commande alternative (si le mot de passe est invalide ou si l'utilisateur annule)
#COMMANDE_BASIC="python3 main.py"

#echo "What command would you like to use to launch the target? Enter 1 or 2"
#CHOIX1="basic command:  python3 main.py"
#CH#OIX2="sudo command (to incraese priority):  sudo nice -n -12 python3 main.py"
#select option in "$CHOIX1" "$CHOIX2"; do
#    case $REPLY in
#        1)
#            echo "Exécution sans sudo..."
#            eval "$COMMANDE_BASIC"    # ← remplace par ta commande sans droits root
#            break
#            ;;
#        2)
#            echo "Exécution avec sudo..."
#            eval "$COMMANDE_SUDO"   # ← remplace par ta commande
#            break
#            ;;
#        3)
#            echo "Fin du script."
#            exit 0
#            ;;
#        *)
#            echo "invalid choise, enter '1' to use basic command or '2' to use 'sudo' command, repeat."
#            ;;
#    esac
#done

