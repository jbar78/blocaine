import sys
sys.path.insert(0, "..")
from opcua import Client

def browse(node, level=0):
    for child in node.get_children():
        print("  " * level, child.get_browse_name(), child.get_nodeId())
        browse(child, level + 1)

if __name__ == "__main__":
    client = Client("opc.tcp://localhost:4840/freeopcua/server/")
    #connect using a user
    # client = Client("opc.tcp://admin@localhost:4840/freeopcua/server/")
    try:
        client.connect()

        # Client has a few methods to get proxy to UA nodes that
        #  should always be in address space such as Root or Objects
        root = client.get_root_node()
        print("Objects node is: ", root)

        # Node objects have methods to read and write node attributes
        #  as well as browse or populate address space
        print("Children of root are: ", root.get_children())

        # get a specific node knowing its node id
        #var = client.get_node(ua.NodeId(1002, 2))
        #var = client.get_node("ns=3;i=2002")
        #print(var)
        #var.get_data_value() # get value of node as a DataValue object
        #var.get_value() # get value of node as a python builtin
        #var.set_value(3.9) # set node value using implicit data type

        # Now getting a variable node using its browse path
        myvar1 = root.get_child(["0:Objects", "2:MyObject", "2:MyVariable1"])
        myvar2 = root.get_child(["0:Objects", "2:MyObject", "2:MyVariable2"])
        obj = root.get_child(["0:Objects", "2:MyObject"])
        while True:
            print("myvar1 is: ", myvar1)
            print("myvar2 is: ", myvar2)
            print("myobj is: ", obj)
            print(myvar1.get_value())
            print(myvar2.get_value())
            print(f"1er variable: nom={myvar1}, nom={obj.get_browse_name()}, valeur={myvar1.get_value()}")
            print(f"2e  variable: nom={myvar2}, nom={obj.get_browse_name()},  valeur={myvar2.get_value()}")

            #objects = client.get_objects_node()
            #browse(objects)

    finally:
        client.disconnect()
