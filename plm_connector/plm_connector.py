#!/usr/bin/env python
"""
Connector for Siemens Product lifecycle management (PLM)
Socket <-> MQTT
"""
import sys
import time
from _socket_controller import SocketReader, SocketWriter
from _mqtt_controller import MQTTPublisher, MQTTSubscriber

# CONFIG
SOCKET_HOST = '193.225.89.35'
SOCKET_DATA_PORT = 5501
SOCKET_FEEDBACK_PORT = 5502
MQTT_BROKER_HOST = "almanac-broker"
MQTT_BROKER_PORT = 1883
MQTT_CLIENTID_PREFIX = "plm_connector_"
MQTT_SUBSCRIBE_TOPIC = "/outgoing/DS[1]:EarlyDetector/+"
# MQTT_SUBSCRIBE_TOPIC = "ceml/output/EarlyDetector"

# Setup sockets
sock_reader = SocketReader(SOCKET_HOST, SOCKET_DATA_PORT)
sock_writer = SocketWriter(SOCKET_HOST, SOCKET_FEEDBACK_PORT)
# Setup MQTT clients
publisher = MQTTPublisher(MQTT_BROKER_HOST, MQTT_BROKER_PORT, MQTT_CLIENTID_PREFIX+str(time.time()))
subscriber = MQTTSubscriber(MQTT_BROKER_HOST, MQTT_BROKER_PORT, MQTT_CLIENTID_PREFIX+str(time.time()))


def outgoingHandler(json_obj):
    result = json_obj['ResultValue']
    # print("ConfusionMatrix: {}, MCC: {}".format(result['evaluationMetrics'][0]['confusionMatrix'], result['evaluationMetrics'][0]['result']))
    if result['prediction']==1:
        sock_writer.send(result['originalInput']['id'])

def incomingHandler(json_obj):
    publisher.publishSENML(json_obj[json_obj.keys()[0]], qos=0)
    sys.stdout.flush()

sock_reader.start(incomingHandler)
sock_writer.send("ping")
subscriber.subscribe(MQTT_SUBSCRIBE_TOPIC, outgoingHandler, qos=0)

while True:
    try:
        time.sleep(.3)
    except KeyboardInterrupt:
        print "\nInterrupted."
        sock_reader.stop()
        subscriber.stop()
        sys.stdout.flush()
        sys.exit()
