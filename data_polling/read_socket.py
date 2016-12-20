"""
Read production-line JSON data stream from socket and forward it to MQTTPublisher
"""
import socket
import re
import json
import paho.mqtt.client as mqtt
import logging
from mqtt_publisher import MQTTPublisher

logging.basicConfig(filename='read_socket.log',level=logging.DEBUG, format='%(asctime)s %(message)s')

# SOCKET
HOST = '193.225.89.35'
PORT = 5501
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

# MQTT
BROKER_HOST = "almanac-broker"
BROKER_PORT = 1883
CLIENT_ID = "socket_forwarder"
mqtt = MQTTPublisher(CLIENT_ID, BROKER_HOST, BROKER_PORT)

# split packet into json strings
def split_packet(data):
	s = re.split(r'>SOM[0-9A-Z]+<', data)
	# trim "\x00" suffix after each json
	for i, msg in enumerate(s):
		s[i] = re.sub('\x00$', '', msg)
	return s, len(s)>1

# iterate through splitted messages, return (if any) partial data
def iterator(data):
	for msg in data:
		json_obj, ok = parse_json(msg)
		if ok:
			handle(json_obj)
		else:
			# partial json string in the end of message
			return msg
	return ''

# parse and validate json
def parse_json(myjson):
	try:
		json_object = json.loads(myjson)
	except ValueError, e:
		return None, False
	return json_object, True

# log lost messages
tracker = -1
def track_loss(json_obj):
	index = int(json_obj.keys()[0])
	global tracker
	# init tracker
	if tracker == -1:
		tracker = index-1

	if tracker+1 != index:
		print("[WARNING] Missing message. Expected: {}, Received: {}".format(tracker+1, index))
		logging.warning("Missing message. Expected: {}, Received: {}".format(tracker+1, index))
	# update tracker
	tracker = index

# handle json object
def handle(json_obj):
	#track_loss(json_obj)
	mqtt.publishSENML(json_obj, qos=0)
	#print(json_obj)


buffer = ''
while True:
	data = s.recv(2048)
	if data:
		data, _ = split_packet(data)
		if data[0] != '':
			msg = buffer+data[0]
			split, multiple = split_packet(msg)
			if multiple:
				iterator(split)
			else:
				buffer = ''
				json_obj, ok = parse_json(msg)
				if ok:
					handle(json_obj)
				else:
					print("[ERROR] Bad data: " + msg)
					logging.debug("Bad data: " + msg)

		buffer = iterator(data[1:])
		#print ""

	else:
		break

s.close()
