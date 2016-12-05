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

url = "http://localhost:5000/predict"
products = {}
def handler(json_string):
	#features = copy.deepcopy(Features)
	j = json.loads(json_string)
	bn = j['ResultValue']['measurements']['bn']
	
	feature_name = j['ResultValue']['measurements']['e'][0]['n']
	if feature_name == "ConAssembly1/Con1Screw" or feature_name == "ConAssembly2/Con2Screw":
		feature_name = "ConAssembly1or2/Con1or2Screw"
	elif feature_name == "PtAssembly2/Pt2" or feature_name == "PtAssembly3/Pt2":
		feature_name = "PtAssembly2or3/Pt2or3"
	
	value = None
	if feature_name == "FunctionTest/Quality_OK":
		value = j['ResultValue']['measurements']['e'][0]['bv']
	else:
		value = j['ResultValue']['measurements']['e'][0]['v']
		
	if bn not in products:
		if feature_name != "ScreenPrinter/PositionX":
			return
		products[bn] = {}
		products[bn]["Id"] = bn
		products[bn]["TotalFeatures"] = 0
	
	products[bn][feature_name] = value
	products[bn]["TotalFeatures"] += 1
	
	print("{}: {}".format(products[bn]["Id"], products[bn]["TotalFeatures"]))
	json_data = json.dumps(products[bn])
	r = requests.post(url, json=json_data)
	print(r)

	
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER_HOST, BROKER_PORT, 60)
client.loop_forever()