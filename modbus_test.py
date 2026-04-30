from pymodbus.client import ModbusTcpClient
import time

#def modbus_conn(client):
def modbus_conn(o0_client_id=None, i0_adresse_ip='127.0.0.1', i1_port=502, i2_timeout=0.2, i3_close=False):
	global i
	def modbus_connection():
		proc_name = "mod_bus_connection: "
		print (proc_name, f"i={i}")
		#ret_client = ModbusTcpClient('127.0.0.1', port=502, timeout=0.2)  # IP esclave
		ret_client = ModbusTcpClient(host=i0_adresse_ip, port=i1_port, timeout=i2_timeout)  # IP esclave
		ret_client.connect()
		print (proc_name, f"après client.connect()={o0_client_id}")
		return ret_client
	proc_name = "mod_bus_conn: "
	#try:
	#	print (proc_name, f"i={i}, test: o0_client_id.connected={o0_client_id.connected}")
	#	if not o0_client_id.connected:
	#		print (proc_name, f"i={i}", "not connected")
	#		return modbus_connection()
	#	else:
	#		print (proc_name, f"i={i}", "connected")
	#		return o0_client_id
	#except:
	#	print (proc_name, f"i={i}", "except")
	#	return modbus_connection()

	print (proc_name, f"i={i}, test: o0_client_id.connected")
	if hasattr(o0_client_id, "connected"):
		print (proc_name, f"i={i},   .connected existe={o0_client_id.connected}")
		if o0_client_id.connected:
			print (proc_name, f"i={i}", "connected")
			return o0_client_id
		else:
			print (proc_name, f"i={i}", "not connected")
			return modbus_connection()
	else:
		print (proc_name, f"i={i}", "not connected")
		return modbus_connection()


def modbus_read(i0_client_id=None, i1_slave=1, i2_fonction=3, i3_adresse=0, i4_count=1):
	if i2_fonction==3:
		read_result = client_id.read_holding_registers(i3_adresse, i4_count, slave=i1_slave)
	return read_result

def modbus_write(i0_client_id=None, i1_slave=1, i2_fonction=3, i3_adresse=0, i4_value=1):
	if i2_fonction==16:
		write_result = client_id.write_registers(i3_adresse, i4_value, i1_slave)
	return write_result


i=0
#client = ModbusTcpClient('127.0.0.1', port=502, timeout=0.2)  # IP esclave
#client.connect()
client_id=None
while 1:
	print ("loop: ", f"i={i}")
	#client=modbus_conn(client)
	client_id =modbus_conn(o0_client_id=client_id, i0_adresse_ip='127.0.0.1', i1_port=502, i2_timeout=0.2, i3_close=False)
	t_début = time.time()
	#read_result = client_id.read_holding_registers(1, 10, slave=1)
	read_result = modbus_read(i0_client_id=client_id, i1_slave=1, i2_fonction=3, i3_adresse=1, i4_count=10)
	t_fin = time.time()
	read_duration = t_fin-t_début
	t_début = time.time()
	#write_result = client_id.write_registers(2, [i], slave=1)
	write_result = modbus_write(i0_client_id=client_id, i1_slave=1, i2_fonction=16, i3_adresse=2, i4_value=[i, i])
	t_fin = time.time()
	write_duration = t_fin-t_début
	print(f"[{i}] ModBus  read: time={read_duration},  ❌Erreur:{read_result.isError()},  registres lu:{read_result.registers}")
	print(f"[{i}] ModBus write: time={write_duration},  ❌Erreur:{write_result.isError()}")
	i+=1
	if i > 0xFFFF: 	i=0
	time.sleep(1)
client.close()