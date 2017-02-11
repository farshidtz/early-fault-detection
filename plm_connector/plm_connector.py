#!/usr/bin/env python
"""
Connector for Siemens Product lifecycle management (PLM)
Socket <-> MQTT
"""
import sys
import time
import uuid
import logging
import argparse
from _socket_controller import SocketReader, SocketWriter
from _mqtt_controller import MQTTPublisher, MQTTSubscriber

# Parse flags
parser = argparse.ArgumentParser(description='Connector for Siemens Product lifecycle management (PLM)')
parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
args = parser.parse_args()

# Setup logging
logging_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s:\t %(message)s')
h = logging.StreamHandler()
h.setFormatter(logging_formatter)
logger = logging.getLogger(__name__)
if args.verbose:
    logger.setLevel(logging.DEBUG)
logger.addHandler(h)

# CONFIG
SOCKET_HOST = '193.224.59.25'
SOCKET_DATA_PORT = 5501
SOCKET_FEEDBACK_PORT = 5502
MQTT_BROKER_HOST = "iot.eclipse.org"
MQTT_BROKER_PORT = 1883
MQTT_CLIENTID_PREFIX = "plm_connector_"
MQTT_SUBSCRIBE_TOPIC = "/outgoing/DS[1]:EarlyDetector/+"
# MQTT_SUBSCRIBE_TOPIC = "ceml/output/EarlyDetector"

# Setup sockets
sock_reader = SocketReader(SOCKET_HOST, SOCKET_DATA_PORT)
sock_writer = SocketWriter(SOCKET_HOST, SOCKET_FEEDBACK_PORT)
# Setup MQTT clients
publisher = MQTTPublisher(MQTT_BROKER_HOST, MQTT_BROKER_PORT, MQTT_CLIENTID_PREFIX+str(uuid.uuid4()))
subscriber = MQTTSubscriber(MQTT_BROKER_HOST, MQTT_BROKER_PORT, MQTT_CLIENTID_PREFIX+str(uuid.uuid4()))


def outgoingHandler(json_obj):
    result = json_obj['ResultValue']
    # print("ConfusionMatrix: {}, MCC: {}".format(result['evaluationMetrics'][0]['confusionMatrix'], result['evaluationMetrics'][0]['result']))
    if result['prediction']==1:
        logger.debug("->PLM {}".format(result['originalInput']['id']))
        sock_writer.send(result['originalInput']['id'])

def incomingHandler(json_obj):
    logger.debug("->Broker {}".format(json_obj))
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
