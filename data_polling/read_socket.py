"""
Read production-line JSON data stream from socket
"""
import socket
import re
import json

HOST = 'localhost'
PORT = 30000
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

# validate json
def is_json(myjson):
	try:
		json_object = json.loads(myjson)
	except ValueError, e:
		return False
	return True

# handle json message
tracker = -1
def handle(msg):
	print(repr(msg))
	index = int(json.loads(msg).keys()[0])
	global tracker
	# init tracker
	if tracker == -1:
		tracker = index-1

	if tracker+1 != index:
		print("ITEM MISSING!!!", tracker, index)
	# update tracker
	tracker = index

# split json objects in a packet
def json_split(data):
	s = re.split(r'>SOM[0-9A-Z]+<', data)
	# trim "\x00" suffix after each json
	for i, msg in enumerate(s):
		s[i] = re.sub('\x00$', '', msg)
	return s, len(s)>1

# iterate through messages in this packet
def iterator(data):
	for msg in data:
		if is_json(msg):
			handle(msg)
		else:
			return msg

buffer = ''
while True:
	data = s.recv(2048)	
	if data:
		data, _ = json_split(data)
		if data[0] != '':
			msg = buffer+data[0]
			split, multiple = json_split(msg)
			if multiple:
				iterator(split)
			else:
				buffer = ''
				if is_json(msg):
					handle(msg)
				else:
					print("[ERROR] BAD DATA: " + msg)

		buffer = iterator(data[1:])
		print ""

	else:
		break

s.close()