"""
Socket Controller Module
For Siemens PLM Plant Simulation 13
- Read and parse JSON data stream from a socket
- Write messages to a socket
"""

import socket
import re
import json
import logging
import time
import threading


class SocketReader:

	def __init__(self, host, port):
		self.host = host
		self.port = port
		self.run_event = threading.Event()
		self.logger = logging.getLogger(__name__)

	# split packet into json strings
	def split_packet(self, data):
		s = re.split(r'>SOM[0-9A-Z]+<', data)
		# trim "\x00" suffix after each json
		for i, msg in enumerate(s):
			s[i] = re.sub('\x00$', '', msg)
		return s, len(s)>1

	# iterate through splitted messages, return (if any) partial data
	def iterator(self, data, handler):
		for msg in data:
			json_obj, ok = self.parse_json(msg)
			if ok:
				handler(json_obj)
			else:
				# partial json string in the end of message
				return msg
		return ''

	# parse and validate json
	def parse_json(self, myjson):
		try:
			json_object = json.loads(myjson)
		except ValueError, e:
			return None, False
		return json_object, True

	# log lost messages
	tracker = -1
	def track_loss(self, json_obj):
		index = int(json_obj.keys()[0])
		# init tracker
		if self.tracker == -1:
			self.tracker = index-1

		if self.tracker+1 != index:
			self.logger.warning("Missing message. Expected: {}, Received: {}".format(self.tracker+1, index))
		# update tracker
		self.tracker = index

	def socketConnect(self):
		socket.setdefaulttimeout(5)
		self.logger.info("Connecting to {}:{}".format(self.host, self.port))
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			self.sock.connect((self.host, self.port))
			self.logger.info("Connected.")
		except Exception as e:
			self.logger.error("connect: {}".format(e))
			#self.logger.info("Will retry in 1s...")
			#time.sleep(1)
			self.socketConnect()


	def worker(self, handler):
		self.logger.info("Listenning...")
		buffer = ''
		retries = 0
		while self.run_event.is_set():
			try:
				data = self.sock.recv(2048)
				retries = 0
			except Exception as e:
				retries = retries+1
				self.logger.error("recv: {} ({})".format(e, retries))
				#self.logger.info("Will retry in 1s...")
				#time.sleep(1)
				#buffer = ''
				if(retries>=5):
					self.logger.info("Restarting the connection...")
					self.stop()
					self.start(self.external_handler)
					return
				continue
			if data:
				data, _ = self.split_packet(data)
				if data[0] != '':
					msg = buffer+data[0]
					split, multiple = self.split_packet(msg)
					if multiple:
						self.iterator(split, handler)
					else:
						buffer = ''
						json_obj, ok = self.parse_json(msg)
						if ok:
							#self.track_loss(json_obj)
							# json_obj[json_obj.keys()[0] is the value of first key {"counter" : <senml>}
							#
							# self.logger.info(json_obj)
							handler(json_obj)
						else:
							self.logger.warning("Bad data: " + msg)

				buffer = self.iterator(data[1:], handler)
				#print ""

			else:
				self.logger.info("Socket disconnected.")
				buffer = ''
				self.socketConnect()

	def start(self, handler):
		self.external_handler = handler
		self.socketConnect()
		self.run_event.set()
		self.t = threading.Thread(target=self.worker, args=(handler,))
		self.t.start()
		self.logger.info("Started.")

	def stop(self):
		self.run_event.clear()
		self.sock.close()
		self.logger.info("Stopped.")

class SocketWriter:
	def __init__(self, host, port):
		self.host = host
		self.port = port
		self.logger = logging.getLogger(__name__)

	def send(self, message):
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.connect((self.host, self.port))
		try:
		    sock.sendall(json.dumps(message))
		finally:
		    sock.close()
