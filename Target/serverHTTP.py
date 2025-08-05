import socket
from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
from PARAM_NETWORK import *
from sharedata import clientsTCP
from compiled import *

html_style ="""<style>
        th,
        td {
          border: 1px solid rgb(160 160 160);
          padding: 8px 10px;
        }

        th[scope="col"] {
          background-color: #505050;
          color: #fff;
        }

        th[scope="row"] {
          background-color: #d6ecd4;
        }

        td {
          text-align: center;
        }

        tr:nth-of-type(even) {
          background-color: #eee;
        }

        table {
          border-collapse: collapse;
          border: 2px solid rgb(140 140 140);
          font-family: sans-serif;
          font-size: 1rem;
          letter-spacing: 1px;
        }

        caption {
          caption-side: bottom;
          padding: 10px;
        }
        </style>
        """
menu = """<table>
        <tr><th>Menu</th></tr>
        <tr><td>
        <a href='/threads'>Task list</a><br>
        <a href='/blocs'>Bloc & Output list</a><br>
        <a href='/connexion'>Connexions</a><br>
        <a href='/list_compiled:print_list_compiled:'>print list_compiled</a><br>
        <a href='/list_threads:print_thread_list:'>print list_threads</a>
        </td></tr>
        </table>
        <br>"""

html_debut = """<html>
            <head>        
            <title>Target</title>
            <meta charset='UTF-8'>"""+html_style+"""
            </head>
            <body>"""
#<meta http-equiv="refresh" content="1"> induit un problème de "hotswap" order" reçu périodiquement ?

html_fin ="</body></html>"


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Cette connexion n'a pas besoin d'être établie réellement
        s.connect(('10.254.254.254', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        proc_name = "do_GET: "
        global httpd
        (ipp, ppp) = httpd.server_address
        print (f"httpd: ip={ipp},   port={ppp}")

        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        local_ip = get_local_ip()
        #print ("self.path=", self.path)
        i = self.path.find(":")
        self.key   = self.path[0:i]
        self._key  = self.path[i+1:]
        #print ("self.key=", self.key)
        #print ("self._key=", self._key)
        i = self._key.find(":")
        self.order   = self._key[0:i]
        self._order  = self._key[i+1:]
        #print ("self.order=", self.order)
        #print ("self._order=", self._order)
        self.bloc_name   = self._order
        #print ("self.key=", self.key)
        #print ("self.order=", self.order)
        #print ("self.bloc_name=", self.bloc_name)
        print ("HTTP: réception: self.key=", self.key, "self.order=", self.order, "self.bloc_name=", self.bloc_name)
        # Gestion des différentes pages
        if self.path == "/" or self.key == "/list_compiled" or self.key == "/list_threads": #__________________menu principal
            if self.key == "/list_compiled":
                print_exeblocs()
            if self.key == "/list_threads":
                print_threads()
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            #self.send_header("Connection", "keep-alive")
            #self.send_header("Keep-Alive", "timeout=5, max=100")
            self.end_headers()
            # Page d'accueil
            html = html_debut
            html +=f"<p>Target: {hostname}     (ip:{local_ip})</p>"
            html += menu
            html += html_fin
            #print ("HTML=", html)
            self.wfile.write(html.encode("utf-8"))

        elif self.path == "/connexion": #__________________liste des conections
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            #self.send_header("Connection", "keep-alive")
            #self.send_header("Keep-Alive", "timeout=5, max=100")
            self.end_headers()
           # Création du contenu HTML
            #hostname = socket.gethostname()
            #local_ip = get_local_ip()
            #local_ip = socket.getsockname()
            client_ip, client_port = self.client_address
            try:
                client_name = socket.gethostbyaddr(client_ip)[0]
            except socket.herror:
                client_name = "'Unknow'"
            html = html_debut
            html +=f"<p>Target: {hostname}     (ip:{local_ip})</p>"
            html += menu
            html +="<table>"
            html += f"""<tr><th colspan="4";>HTTP protocol</th></tr>"""
            html += f"""<tr><th>...</th><th>@ip</th><th>port</th><th>Host name</th></tr>"""
            html += f"""<tr><th>Server</th><td>{local_ip}</td><td>{PARAM_HTTP_PORT}</td><td>{hostname}</td></tr>"""
            html += f"""<tr><th>Last Client</th><td>{client_ip}</td><td>{client_port}</td><td>{client_name}</td></tr>"""
            html +="</table>"
            html +="<p></p>"
            html +="<table>"
            html += f"""<tr><th colspan="3";>TCP/IP protocol</th></tr>"""
            html += f"""<tr><th>...</th><th>@ip</th><th>port</th></tr>"""
            #html += f"""<tr><th>server</th><td>{PARAM_TCP_HOST_IP}</td><td>{PARAM_TCP_HOST_PORT}</td></tr>"""
            html += f"""<tr><th>server</th><td>{local_ip}</td><td>{PARAM_TCP_HOST_PORT}</td></tr>"""
            for i, client in enumerate(clientsTCP):
                html += f"""<tr><th>client[{i}]</th><td>{client[0]}</td><td>{client[1]}</td></tr>"""
            html +="</table>"
            html +="<a href='/connexion'>Refresh</a>"
            html += html_fin
            #print ("HTML=", html)
            self.wfile.write(html.encode())

        elif self.path == "/threads": #____________________________liste des threads
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            #self.send_header("Connection", "keep-alive")
            #self.send_header("Keep-Alive", "timeout=5, max=100")
            self.end_headers()
            # page: thread list
            html = html_debut
            html +=f"<p>Target: {hostname}     (ip:{local_ip})</p>"
            html += menu
            html +="<table>"
            html += f"""<tr><th colspan="9";>Task list</th></tr>"""
            html += f"""<tr><th colspan="3"; style="vertical-align: bottom;">Setting</th><th colspan="6";>Feedback</th></tr>"""
            html += f"""<tr><th>name</th><th>id</th><th>period</th><th>cycle time</th><th>cycle time<br>min</th><th>cycle time<br>max</th><th>counter</th><th>number of<br>output</th><th>CPU load</th></tr>"""
            for i, thread in enumerate(list_threads):
                if thread['period'] < 1:
                    txt_period = f"{1000*thread['period']:3.0f}ms"
                    txt_cycle  = f"{1000*thread['cycle_time']:3.3f}ms"
                    txt_cycle_min = f"{1000*thread['min_max']['min']:3.3f}ms"
                    txt_cycle_max = f"{1000*thread['min_max']['max']:3.3f}ms"
                else:
                    txt_period = f"{thread['period']}s"
                    txt_cycle  = f"{thread['cycle_time']:3.6f}s"
                    txt_cycle_min = f"{thread['min_max']['min']:3.6f}s"
                    txt_cycle_max = f"{thread['min_max']['max']:3.6f}s"
                nbr_output = 0
                for exe in thread['list_exe']:
                    if exe['run']:
                        nbr_output += 1
                txt_nbr_output = f"{nbr_output}"
                html += "<tr>"
                html += f"<td>{thread['name']}</td><td>{thread['id']}</td><td>"+txt_period+"</td>"
                html += "<td>"+txt_cycle+"</td><td>"+txt_cycle_min+"</td><td>"+txt_cycle_max+f"</td><td>{thread['counter']}</td><td>"+txt_nbr_output+f"</td><td>{thread['load_%']:2.3f}%</td>"
                html += "</tr>"
                thread['min_max']['min'] = thread['cycle_time']
                thread['min_max']['max'] = thread['cycle_time']
            html +="</table>"
            thread_load = 0
            for thread in list_threads:
                thread_load += thread['load_%']
            html +=f"User tasks CPU load = {thread_load:3.2f}%<br>"
            html +="<a href='/threads'>Refresh</a>"
            html += html_fin
            #print ("HTML=", html)
            self.wfile.write(html.encode("utf-8"))

        elif self.path == "/blocs" or self.key == "/order": #____________________liste des blocs
            if self.key == "/order":
                print ("Key=", self.key, "  order=", self.order, "  bloc name=", self.bloc_name)
                if self.order == "Run":         run_exebloc(self.bloc_name)
                if self.order == "Stop":        stop_exebloc(self.bloc_name)
                if self.order == "HotSwap":     hot_swap_exebloc(self.bloc_name)
                if self.order == "ColdSwap":    cold_swap_exebloc(self.bloc_name)
                if self.order == "Delete":      delete_exebloc(self.bloc_name)
                if self.order == "Initialize":  init_exebloc(self.bloc_name)
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            #self.send_header("Connection", "keep-alive")
            #self.send_header("Keep-Alive", "timeout=5, max=100")
            self.end_headers()
            # page: thread list
            html = html_debut
            html +=f"<p>Target: {hostname}     (ip:{local_ip})</p>"
            html += menu
            html +="<table>"
            html += f"""<tr><th colspan="5">bloc list</th></tr>"""
            html += f"""<tr><th rowspan="2">bloc<br>name</th><th colspan="2">status</th><th rowspan="2">order</th></tr>"""
            html += f"""<tr><th>shift A</th><th>shift B</th></tr>"""
            html += f"""<tr></tr>"""
            list_blocs = compiled_status()
            for i, lb in enumerate(list_blocs):
                html += "<tr>"
                html += f"<td>{lb['name']}</td><td>{lb['status_A']}</td><td>{lb['status_B']}</td><td>{lb['orders']}</td>"
                html += "</tr>"
            html +="</table>"

            html +="<br>"
            html +="<table>"
            html += f"""<tr><th colspan="10">bloc output list</th></tr>"""
            html += f"""<tr><th colspan="3">bloc</th><th colspan="4">output</th><th rowspan="2">status</th><th colspan="2">task</th></tr>"""
            html += f"""<tr><th>name</th><th>shift</th><th>building time  <span style="font-size: 80%;">(yyyy/mm/dd)</span></th><th>name</th><th>id</th><th>value</th><th>validity</th><th>name</th><th>id</th></tr>"""
            for thread in list_threads:
                for exe in thread['list_exe']:
                    if exe['run']:
                        txt_status = "Running"
                        txt_value = exe['exebloc'].sublocs[exe['iesubloc']].inputs[0]['var']
                        if exe['exebloc'].sublocs[exe['iesubloc']].inputs[0]['valide']:
                            txt_validity = "😊"
                            txt_style = ""
                        else:
                            txt_validity = "☠ "
                            txt_style = f"""style="font-size: 200%;" """
                    else:
                        txt_status = "Down"
                        txt_value = txt_validity = "..."
                        txt_style = ""
                    txt_building= exe['exebloc'].header['building'].strftime("%Y/%m/%d  - %H:%M:%S")
                    html += "<tr>"
                    html += f"<td>{exe['exebloc'].header['name']}</td><td>{exe['exebloc'].header['AB']}</td><td>"+txt_building+"</td>"
                    html += f"<td>{exe['exebloc'].sublocs[exe['iesubloc']].inputs[0]['name']}</td><td>{exe['exebloc'].sublocs[exe['iesubloc']].header['id']}</td>"
                    html += f"""<td>{txt_value}</td><td """+txt_style+f""">{txt_validity}</td>"""
                    html += f"<td>{txt_status}</td>"
                    html += f"<td>{thread['name']}</td><td>{thread['id']}</td>"
                    html += "</tr>"
            html +="</table>"
            html +="<a href='/blocs'>Refresh</a>"
            html += html_fin
            self.wfile.write(html.encode("utf-8"))
        else:
            self.send_response(404)
            self.send_header("Content-type", "text/html")
            #self.send_header("Connection", "keep-alive")
            #self.send_header("Keep-Alive", "timeout=5, max=100")
            self.end_headers()
            # Page d'erreur 404
            html = """
            <html>
                <head><title>404 - Page not found</title></head>
                <body>
                    <h1>Error 404</h1>
                    <p>this page does not exist</p>
                    <a href="/">Return</a>
                </body>
            </html>
            """
            self.wfile.write(html.encode("utf-8"))

#def run_serverHTTP(port=PARAM_HTTP_PORT):
#    with socketserver.TCPServer(("", port), MyServer) as httpd:
#        print(f"active server on port: {port}")
#        httpd.allow_reuse_address = True 
#        httpd.serve_forever()

def run_serverHTTP(server_class=HTTPServer, handler_class=MyServer, port=PARAM_HTTP_PORT):
    global httpd
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting server on port {port}...")
    httpd.allow_reuse_address = True 
    (ipp, ppp) = httpd.server_address
    print (f"httpd: ip={ipp},   port={ppp}")
    httpd.serve_forever()
