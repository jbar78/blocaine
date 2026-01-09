from pymodbus.client import ModbusTcpClient
from time import time

client = ModbusTcpClient('127.0.0.1')  # IP esclave
client.connect()
for i in range(0,1000):
	t_début = time()
	result = client.read_holding_registers(10, 20, slave=1)
	t_fin = time()
	print(f"[{i}] Registers: ", result.registers, f",   durée:{t_fin-t_début}")
	result = client.write_registers(0, [3, 3], slave=1)
client.close()