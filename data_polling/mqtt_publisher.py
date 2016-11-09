import paho.mqtt.client as mqtt
import json

class MQTTPublisher:
	
	def __init__(self, client_id, host, port):
		self.mqttc = mqtt.Client(client_id)
		self.mqttc.connect(host, port)
		
	def publish(self, json_obj):
		senml = json_obj[json_obj.keys()[0]]
		self.mqttc.publish(senml['bn'], json.dumps(senml, separators=(',', ':')), qos=1)
		self.mqttc.loop()