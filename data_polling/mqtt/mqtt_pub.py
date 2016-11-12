import paho.mqtt.client as mqtt


mqttc = mqtt.Client("python_pub")
mqttc.connect("localhost", 1883)
i = 0
while True:
	i += 1
	mqttc.publish("hello/world", "Hello, World! "+str(i), qos=1)
	mqttc.loop()