import paho.mqtt.client as mqtt
import json

class MQTTPublisher:

	def __init__(self, host, port, client_id=None):
		self.client = mqtt.Client(client_id)
		self.client.connect(host, port)

	# de-serialize and publish json
	def publish(self, topic, json_obj, qos=0):
		self.client.publish(topic, json.dumps(json_obj, separators=(',', ':')), qos=qos)
		self.client.loop()

	# de-serialize and publish senml object with 'bn' as topic
	def publishSENML(self, senml, qos=0):
		self.client.publish(senml['bn'], json.dumps(senml, separators=(',', ':')), qos=qos)
		self.client.loop()

class MQTTSubscriber:

	def __init__(self, host, port, topic, handler, qos=0, client_id=None):
		self.topic = topic
		self.handler = handler
		self.qos = qos

		self.client = mqtt.Client(client_id)
		self.client.on_connect = self.on_connect
		self.client.on_message = self.on_message
		self.client.connect(host, port)
		self.client.loop_forever()

	# The callback for when the client receives a CONNACK response from the server.
	def on_connect(client, userdata, rc):
		client.subscribe(self.topic, qos=self.qos)

	# The callback for when a PUBLISH message is received from the server.
	def on_message(client, userdata, msg):
		print "Topic: ", msg.topic+'\nMessage: '+str(msg.payload)
		self.handler(json.loads(msg.payload))
