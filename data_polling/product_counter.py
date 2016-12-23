import paho.mqtt.client as mqtt
import json

BROKER_HOST = "almanac-broker"
BROKER_PORT = 1883

def on_connect(client, userdata, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("SMTLine/#", qos=0)

products = {}
counter = 0
def on_message(client, userdata, msg):
    global counter
    senml = json.loads(msg.payload)
    bn = senml['bn']
    n = senml['e'][0]['n']

    if bn in products:
        if n == 'FunctionTest/Quality_OK':
            products[bn]["label"] = senml['e'][0]['bv']
            counter+=1
            print counter, products[bn]
            return
        products[bn]["features"]+=1
    else:
        if n == 'Source/ProdType':
            products[bn]= {
                "id": bn,
                "features" : 0,
                "label": None
                }


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER_HOST, BROKER_PORT, 60)
client.loop_forever()
