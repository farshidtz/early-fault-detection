import paho.mqtt.client as mqtt
import json
import requests

BROKER_HOST = "almanac-broker"
BROKER_PORT = 1883

def on_connect(client, userdata, rc):
	print("Connected with result code "+str(rc))
	client.subscribe("/outgoing/#", qos=1)

def on_message(client, userdata, msg):
	handler(msg.payload)


"""
{
	"Time": "2016-12-05T16:15:24.767Z",
	"ResultValue": {
		"type": {
			"bn": "SMTLine/B202/P29024518/",
			"bt": 2294515740,
			"e": [{
					"sv": "ABU2",
					"n": "Source/ProdType",
					"t": 1480950917726
				}
			]
		},
		"measurements": {
			"bn": "SMTLine/B202/P29024518/",
			"bt": 2294516580,
			"e": [{
					"u": "mm",
					"n": "ScreenPrinter/PositionY",
					"v": 199.91,
					"t": 1480950924767
				}
			]
		}
	},
	"ResultType": "Map",
	"Datastream": {
		"id": "f1a0df75-eb26-4d24-9d8d-3a0a68e86f86"
	},
	"Sensor": {
		"id": "f1a0df75-eb26-4d24-9d8d-3a0a68e86f86"
	}
}
"""

import socket
import sys
HOST = '193.225.89.35'
PORT = 5502
# HOST = 'localhost'
# PORT = 9999
def send_feedback(id):
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect((HOST, PORT))
	try:
	    sock.sendall(id)
	finally:
	    sock.close()

from _agent import Agent
agent = {}

# configure model
config = {
	"trainfile" : "ABU1.txt",
	"model" : "random_forest",
	"model_conf" : {},
	"trained_model": "tmp"
}
# r = requests.post("http://localhost:5000/build", json=json.dumps(config))
# print(r)
agent = Agent(config)
agent.pre_train()

products = {}
def handler(json_string):
	#features = copy.deepcopy(Features)
	j = json.loads(json_string)
	bn = j['ResultValue']['measurements']['bn']
	feature_name = j['ResultValue']['measurements']['e'][0]['n']

	# new product
	if bn not in products:
		# start from the beginning only
		if feature_name != "ScreenPrinter/PositionX":
			return
		products[bn] = {"ResultValue":{}}
		products[bn]["ResultValue"]["type"] = j['ResultValue']['type']
		products[bn]["ResultValue"]["measurements"] = {
			"bn": bn,
			"e": []
		}
		products[bn]["ResultValue"]["total"] = 0
		products[bn]["ResultValue"]["current_station"] = j['ResultValue']['type']['e'][0]['n']

	# FunctionTest/Quality_OK is in "measurements" here rather than "label"
	if feature_name == "FunctionTest/Quality_OK":
		products[bn]["ResultValue"]["label"] =  j['ResultValue']['measurements']
	else:
		products[bn]["ResultValue"]["measurements"]["e"].append( j['ResultValue']['measurements']['e'][0] )
		products[bn]["ResultValue"]["total"] += 1

	# keep track of stations
	station = feature_name.partition('/')[0]
	prev_station = products[bn]["ResultValue"]["current_station"]
	products[bn]["ResultValue"]["current_station"] = station

	if prev_station != station:
		# print(feature_name)
		print("{} @{} Measurements: {}".format(products[bn]["ResultValue"]["type"]['bn'], station, products[bn]["ResultValue"]["total"]))
		json_data = json.dumps(products[bn])
		# r = requests.post("http://localhost:5000/predict", json=json_data)
		# print("Status: {} Response: {}".format(r.status_code, r.json()))
		res = agent.predict(json_data)
		print("Response: {}".format(res))
		if res['prediction'] == 1:
			send_feedback(bn)


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER_HOST, BROKER_PORT, 60)
client.loop_forever()
