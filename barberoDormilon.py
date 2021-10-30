import threading
import time
import random
import keyboard
import queue # módulo queue para get y put, seguro de usar.

BARBEROS = 1 # monto de BARBEROS, se puede cambiar.
CLIENTES = 100 # monto de CLIENTES, se puede cambiar.
ASIENTOS = 4 # monto de ASIENTOS en la sala de espera, se puede cambiar.
ESPERAS = 1 # usar múltiplo de random.random() para que CLIENTES lleguen.

def espera(): # simula el arribo de CLIENTES a tiempo al azar.
	time.sleep(ESPERAS * random.random())

class Barbero(threading.Thread):
	condicion = threading.Condition() # con esto se despierte/duerme el barbero.
	alto_completo = threading.Event() # para cuando todos los CLIENTES han sido atendidos.

	def __init__(self, ID):
		super().__init__()
		self.ID = ID	# ID del barbero en caso de agregar más de 1.


	def run(self):
		while True:
			try:	# uar un try & except es mejor que revisar tamaño de queue, pues queue.qsize() no es seguro con hilos.
				cliente_actual = sala_espera.get(block=False) # block=false para que el hilo no espere/bloquee para obtener unn espacio en la queue.
			except queue.Empty: # se lanza cuando sala_espera está llena.
				if self.alto_completo.is_set(): # alto_completo se actica sólo cuando CLIENTES han sido atendidos completamente.
					return

				print(f"El barbero {self.ID} está durmiendo... Zzz... Zzz... ") # sin CLIENTES, va a dormir.
				with self.condicion:
					self.condicion.wait() # duerme y espera para que el cliente lo despierte.
			else:
				cliente_actual.cortar(self.ID) # corta el cabello de CLIENTES.

class Cliente(threading.Thread):
	DURACION_CORTE = 5

	def __init__(self, ID):
		super().__init__()
		self.ID = ID

	def corte(self): # simula el corte de cabello.
		time.sleep(self.DURACION_CORTE * random.random())

	def cortar(self, id_barbero):  # llamado desde el hilo Barbero.
		print(f"El barbero {id_barbero} está cortando el cabello del cliente {self.ID}")
		self.corte() # "get" a corte.
		print(f"El Barbero {id_barbero} terminó de cortar el cabello al cliente {self.ID}")
		self.atendido.set() # "set" atendido para que el cliente deje la barbería.

	def run(self):
		self.atendido = threading.Event()

		try:	# revisa si hay espacio en sala_espera.
			sala_espera.put(self, block=False)
		except queue.Full: # sin espacio en sala_espera se va.
			print(f"La sala de espera está llena, {self.ID} se fue...")
			return

		print(f"El cliente {self.ID} se sentó en la sala de espera.")
		with Barbero.condicion:
			Barbero.condicion.notify(1) # despierta al barbero.

		self.atendido.wait() # espera para "get" un corte y se retira.


if __name__ == "__main__":
	TODOS_CLIENTES = []          # lista de todos CLIENTES a atender.
	sala_espera = queue.Queue(ASIENTOS) # tamaño maximo de ASIENTOS, elimina la necesidad de Queue.qsize() antes de Queue.put()

	for i in range(BARBEROS): # crea el hilo barbero.
		hilo_barbero = Barbero(i)
		hilo_barbero.start()

	for i in range(CLIENTES): # crea el hilo cliente.
		espera()
		cliente = Cliente(i)
		TODOS_CLIENTES.append(cliente)
		cliente.start()

	for cliente in TODOS_CLIENTES:
		cliente.join()  # espera para salide de todos CLIENTES.

	time.sleep(0.1) # se coloca esto para darle tiempo suficiente al barbero para limpiar tras el cliente final.
	Barbero.alto_completo.set() # permite finalizar el trabajo del barbero.
	with Barbero.condicion:
		Barbero.condicion.notify_all() # despierta en caso de que alguno esté dormido para terminar.
	
	print("La Barbería está cerrada.")
	keyboard.wait("esc")
