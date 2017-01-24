import time
time.sleep(3)

import Pyro4
nameserver = Pyro4.locateNS()
uri = nameserver.lookup("python-agent-0")
print(uri)
agent = Pyro4.Proxy(uri)
print(agent)
try:
    agent.build({"a":123})
except Exception as e:
    print(e)
	

import signal
signal.pause()
