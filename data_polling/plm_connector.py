"""
Connector for Siemens Product lifecycle management (PLM)
Socket <-> MQTT
"""
import sys
import time
from socket_reader import SocketReader, SocketWriter
from mqtt_controller import MQTTPublisher, MQTTSubscriber

# CONFIG
SOCKET_HOST = '193.225.89.35'
SOCKET_DATA_PORT = 5501
SOCKET_FEEDBACK_PORT = 5502
MQTT_BROKER_HOST = "almanac-broker"
MQTT_BROKER_PORT = 1883
MQTT_CLIENTID_PREFIX = "plm_connector_"
MQTT_SUBSCRIBE_TOPIC = "/outgoing/#"

# Setup Socket writer
sock_writer = SocketWriter(SOCKET_HOST, SOCKET_FEEDBACK_PORT)
sock_writer.send("test")
def outgoingHandler(json_obj):
    sock_writer.send(json_obj)

# Setup MQTT publisher
publisher = MQTTPublisher(MQTT_BROKER_HOST, MQTT_BROKER_PORT, MQTT_CLIENTID_PREFIX+str(time.time()))
subscriber = MQTTSubscriber(MQTT_BROKER_HOST, MQTT_BROKER_PORT, MQTT_CLIENTID_PREFIX+str(time.time()))
subscriber.subscribe(MQTT_SUBSCRIBE_TOPIC, outgoingHandler, qos=0)


def incomingHandler(json_obj):
    # global mqtt
    # print(json_obj)
    publisher.publishSENML(json_obj[json_obj.keys()[0]], qos=0)
    sys.stdout.flush()

# Setup Socket reader
sock_reader = SocketReader(SOCKET_HOST, SOCKET_DATA_PORT)
sock_reader.start(incomingHandler)


while True:
    try:
        time.sleep(.3)
        pass
    except KeyboardInterrupt:
        print "Interrupted."
        sock_reader.stop()
        subscriber.stop()
        sys.exit()
