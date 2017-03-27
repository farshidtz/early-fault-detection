import paho.mqtt.client as mqtt
from time import sleep

mqttc = mqtt.Client("python-offline-publisher")
mqttc.connect("localhost", 1883)
#mqttc.loop_forever()

with open("D:/smtline-161117-0.05fr_0.txt") as f:
    for line in f:
		#print(line.strip('\n'))
		mqttc.publish("offline/data", line.strip('\n'), qos=2)
		mqttc.loop()
		#sleep(0.001)
