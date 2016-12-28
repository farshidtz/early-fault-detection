"""
MQTT Controller
A high level MQTT client built on top of paho.mqtt.client
"""

import paho.mqtt.client as mqtt
import json
import logging

logging_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s:\t %(message)s')
h = logging.StreamHandler()
h.setFormatter(logging_formatter)
loggingLevel = logging.DEBUG

class MQTTPublisher:

	def __init__(self, host, port, client_id=None):
		self.client = mqtt.Client(client_id)
		self.client.connect(host, port)
		self.logger = logging.getLogger(__name__)
		self.logger.setLevel(loggingLevel)
		self.logger.addHandler(h)

	# de-serialize and publish json
	def publish(self, topic, json_obj, qos=0):
		self.client.publish(topic, json.dumps(json_obj, separators=(',', ':')), qos=qos)
		self.client.loop()

	# de-serialize and publish senml object with 'bn' as topic
	def publishSENML(self, senml, qos=0):
		self.client.publish(senml['bn'], json.dumps(senml, separators=(',', ':')), qos=qos)
		self.client.loop()

class MQTTSubscriber:

	def __init__(self, host, port, client_id=None):
		self.host = host
		self.port = port
		self.client = mqtt.Client(client_id)

		self.logger = logging.getLogger(__name__)
		self.logger.setLevel(loggingLevel)
		self.logger.addHandler(h)

	def subscribe(self, topic, handler, qos=0):
		self.topic = topic
		self.handler = handler
		self.qos = qos
		self.client.on_connect = self.on_connect
		self.client.on_message = self.on_message
		self.client.connect(self.host, self.port)
		self.client.loop_start()
		self.logger.info("Subscribed to %s" % topic)

	# The callback for when the client receives a CONNACK response from the server.
	def on_connect(self, master, client, userdata, rc):
		self.client.subscribe(self.topic, qos=self.qos)

	# The callback for when a PUBLISH message is received from the server.
	def on_message(self, client, userdata, msg):
		try:
			# user-defined handler
			self.handler(json.loads(msg.payload))
		except Exception as ex:
			self.logger.info("Topic: %s Message: %s" % (msg.topic, str(msg.payload)))
			self.logger.error(ex)

	def stop(self):
		self.client.loop_stop()
		self.client.disconnect()
		self.logger.info("Stopped.")
