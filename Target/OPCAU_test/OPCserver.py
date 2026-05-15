import sys
#sys.path.insert(0, "../..")
import time
from opcua import ua as OPC_ua, Server as OPC_Server



if __name__ == "__main__":

    # setup our server
    serverOPC = OPC_Server()
    serverOPC.set_endpoint("opc.tcp://0.0.0.0:4840/freeopcua/server/")

    # setup our own namespace, not really necessary but should as spec
    uri = "urn:Blocaine:serveur:opcua"
    idx = serverOPC.register_namespace(uri)
    print(f"idx={idx}")

    # get Objects node, this is where we should put our nodes
    objects = serverOPC.get_objects_node()

    # populating our address space
    myobj = objects.add_object(idx, "MyObject")
    myvar0 = myobj.add_variable(idx, "MyVariable0", True)
    myvar0.set_writable()    # Set MyVariable to be writable by clients
    myvar1 = myobj.add_variable(idx, "MyVariable1", 6.7)
    myvar2 = myobj.add_variable(idx, "MyVariable2", 99.7)

    obj_RM_Pump1 = objects.add_object(idx, "RM_pompe1")
    var_RM_Pump1_Cmd_Start = obj_RM_Pump1.add_variable(idx, "Cmd_Start", False)
    var_RM_Pump1_Cmd_Start.set_writable()    # Set MyVariable to be writable by clients
    var_RM_Pump1_Cmd_Stop = obj_RM_Pump1.add_variable(idx, "Cmd_Stop", False)
    var_RM_Pump1_Cmd_Stop.set_writable()    # Set MyVariable to be writable by clients
    var_RM_Pump1_Running = obj_RM_Pump1.add_variable(idx, "Running", False)
    #var_RM_Pump1_IP = obj_RM_Pump1.add_variable(idx, "Cond_initiale", False)
    #var_RM_Pump1_PP = obj_RM_Pump1.add_variable(idx, "Cond_permanent", False)
    #var_RM_Pump1_EP = obj_RM_Pump1.add_variable(idx, "Cond_end", False)
    #var_RM_Pump1_IP_txt0 = obj_RM_Pump1.add_variable(idx, "txt_IP0", "Power missing")
    #var_RM_Pump1_IP_txt1 = obj_RM_Pump1.add_variable(idx, "txt_IP1", "Contactor open")
    #var_RM_Pump1_IP0 = obj_RM_Pump1.add_variable(idx, "IP0", False)
    #var_RM_Pump1_IP1 = obj_RM_Pump1.add_variable(idx, "IP1", False)
    #var_RM_Pump1_PP_txt0 = obj_RM_Pump1.add_variable(idx, "txt_PP0", "Feedback missing")
    #var_RM_Pump1_PP_txt1 = obj_RM_Pump1.add_variable(idx, "txt_PP1", "Power missing")
    #var_RM_Pump1_PP0 = obj_RM_Pump1.add_variable(idx, "PP0", False)
    #var_RM_Pump1_PP1 = obj_RM_Pump1.add_variable(idx, "PP1", False)

    # starting!
    serverOPC.start()

    try:
        count = 0
        while True:
            time.sleep(1)
            count += 0.1
            myvar1.set_value(count)
            myvar2.set_value(count+100)
            if var_RM_Pump1_Cmd_Start.get_value():
                var_RM_Pump1_Cmd_Start.set_value(False)
                var_RM_Pump1_Running.set_value(True)
                print("set")
            if var_RM_Pump1_Cmd_Stop.get_value():
                var_RM_Pump1_Cmd_Stop.set_value(False)
                var_RM_Pump1_Running.set_value(False)
                print("reset")
    finally:
        #close connection, remove subscriptions, etc
        serverOPC.stop()