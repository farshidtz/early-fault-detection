#!/usr/bin/env python
"""
Connector for Siemens Product lifecycle management (PLM)
Socket <-> MQTT
"""
import sys, time, uuid, logging, argparse, json
from _socket_controller import SocketReader, SocketWriter
from _mqtt_controller import MQTTPublisher, MQTTSubscriber

# Parse flags
parser = argparse.ArgumentParser(description='Connector for Siemens Product lifecycle management (PLM)')
parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
parser.add_argument("-c", "--conf", help="path to config file", required=True)
args = parser.parse_args()

# Setup logging
log_level = logging.INFO
# TODO: enable debug with environment variable
if args.verbose:
    log_level = logging.DEBUG
logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s: %(message)s', level=log_level)
logger = logging.getLogger(__file__)

# Load configurations
with open(args.conf, 'r') as f:
    conf = json.load(f)

# Setup sockets
sock_reader = SocketReader(conf['plm_socket']['host'], conf['plm_socket']['data_port'])
sock_writer = SocketWriter(conf['plm_socket']['host'], conf['plm_socket']['feedback_port'])
# Setup MQTT clients
publisher = MQTTPublisher(conf['mqtt']['broker_host'], conf['mqtt']['broker_port'], conf['mqtt']['clientid_prefix']+str(uuid.uuid4()))
subscriber = MQTTSubscriber(conf['mqtt']['broker_host'], conf['mqtt']['broker_port'], conf['mqtt']['clientid_prefix']+str(uuid.uuid4()))


def outgoingHandler(json_obj):
    try:
        # result = json_obj['LastPrediction']
        result = json_obj['ResultValue']
        pid = result['originalInput']['id']
        ptype = result['originalInput']['type']
        prediction = result['prediction']
        # model = json_obj['Model']
        # mcc = model['Evaluator']['WindowEvaluators'][0]['evaluationAlgorithms']['MatthewsCorrelationCoefficient']['result']
        # scm = model['Evaluator']['WindowEvaluators'][0]['sequentialConfusionMatrix'][0]
        # logger.debug("Prediction for {}:{} with MCC:{:0.2f} SCM:{} -> {}".format(ptype, result['originalInput']['id'], mcc, scm, prediction))
        logger.debug("Prediction for {}:{}-> {}".format(ptype, result['originalInput']['id'], prediction))
        if prediction==1:
            s = pid.split('/')
            s.insert(2, ptype)
            s.insert(len(s)-1, str(prediction))
            pid = '/'.join(s)
            logger.info("Sending feedback->PLM {}".format(pid))
            sock_writer.send(pid)
    except KeyError as e:
        logger.error("Key not found: {}".format(e))

def incomingHandler(json_obj):
    #logger.debug("->Broker {}".format(json_obj))
    publisher.publishSENML(json_obj[json_obj.keys()[0]], qos=conf['mqtt']['pub_data_qos'])
    sys.stdout.flush()

sock_reader.start(incomingHandler)
subscriber.subscribe(conf['mqtt']['feedback_topic'], outgoingHandler, qos=conf['mqtt']['sub_feedback_qos'])

while True:
    try:
        time.sleep(.3)
    except KeyboardInterrupt:
        print "\nInterrupted."
        sock_reader.stop()
        subscriber.stop()
        sys.stdout.flush()
        sys.exit()
