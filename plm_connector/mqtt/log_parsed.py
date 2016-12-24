import paho.mqtt.client as mqtt
import json

BROKER_HOST = "almanac-broker"
BROKER_PORT = 1883

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, rc):
	print("Connected with result code "+str(rc))
	# Subscribing in on_connect() means that if we lose the connection and
	# reconnect then subscriptions will be renewed.
	client.subscribe("/outgoing/#", qos=2)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
	print 'Message: '+str(msg.payload)
	j = json.loads(msg.payload)
	type = j['ResultValue']['type']['e'][0]['sv']
	print(type)
	with open(type+".txt", "a") as myfile:
		myfile.write(msg.payload+'\n')

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER_HOST, BROKER_PORT, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()