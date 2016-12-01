import paho.mqtt.client as mqtt
from time import sleep

mqttc = mqtt.Client("python-offline-publisher")
mqttc.connect("almanac-broker", 1883)

with open("data.txt") as f:
    for line in f:
		#print(line)
		mqttc.publish("offline/data", line.strip('\n'), qos=2)
		mqttc.loop()
		sleep(0.001)
