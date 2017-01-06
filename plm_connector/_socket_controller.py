"""
Socket Controller Module
Tweaked for Siemens Plant Simulation 13
- Read and parse JSON data stream from a socket
- Write messages to a socket
"""

import socket
import re
import json
import logging
import time
import threading

logging_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s:\t %(message)s')
h = logging.StreamHandler()
h.setFormatter(logging_formatter)
loggingLevel = logging.DEBUG

class SocketReader:

	def __init__(self, host, port):
		self.host = host
		self.port = port
		self.run_event = threading.Event()
		self.logger = logging.getLogger(__name__)
		self.logger.setLevel(loggingLevel)
		self.logger.addHandler(h)

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
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.connect((self.host, self.port))

	def worker(self, handler):
		buffer = ''
		while self.run_event.is_set():
			data = self.sock.recv(2048)
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
							self.logger.debug("Bad data: " + msg)

				buffer = self.iterator(data[1:], handler)
				#print ""

			else:
				self.logger.debug("Socket disconnected.")
				self.socketConnect()

	def start(self, handler):
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
		self.logger.setLevel(loggingLevel)
		self.logger.addHandler(h)

	def send(self, message):
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.connect((self.host, self.port))
		try:
		    sock.sendall(json.dumps(message))
		finally:
		    sock.close()
