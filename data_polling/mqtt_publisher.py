import paho.mqtt.client as mqtt
import json

class MQTTPublisher:

	def __init__(self, client_id, host, port):
		self.mqttc = mqtt.Client(client_id)
		self.mqttc.connect(host, port)

	# de-serialize and publish json
	def publish(self, topic, json_obj, qos=0):
		self.mqttc.publish(topic, json.dumps(json_obj, separators=(',', ':')), qos=qos)
		self.mqttc.loop()

	# de-serialize and publish senml object with 'bn' as topic
	def publishSENML(self, senml, qos=0):
		self.mqttc.publish(senml['bn'], json.dumps(senml, separators=(',', ':')), qos=qos)
		self.mqttc.loop()
