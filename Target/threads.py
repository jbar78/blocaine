import threading
PARAM_PERIOD_OFFSET = -0.0004 # en seconde

class Intervallometre(threading.Thread):
    def __init__(self, fonction, args=[]):
        threading.Thread.__init__(self)
        print ("thread__init__", args[0]['period'], "(s)")
        self.duree = args[0]['period'] + PARAM_PERIOD_OFFSET
        self.fonction = fonction
        self.args = args
        #self.kwargs = kwargs
        self.encore = True

    def run(self):
        print ("thread__run__", self.args[0]['period'], "(s)")
        while self.encore:
            #print ("thread__run_while__")
            self.timer = threading.Timer(self.duree, self.fonction, self.args)
            self.timer.setDaemon(True)
            self.timer.start()
            self.timer.join()

    def stop(self):
        print ("thread__stop__", self.args[0]['period'], "(s)")
        self.encore = False
        if self.timer.isAlive():
            self.timer.cancel()
