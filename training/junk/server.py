from flask import Flask, request
import json

app = Flask(__name__)
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

from _agent import Agent
agent = {}

""" HANDLERS """
@app.route("/build", methods=["POST"])
def build_handler():
	return json.dumps(build(json.loads(request.json)))

@app.route("/learn", methods=["POST"])
def train_handler():
	return json.dumps(learn(request.json))

@app.route("/predict", methods=["POST"])
def predict_handler():
	return json.dumps(predict(request.json))

""" CONTROLLERS """
def build(j):
	global agent
	agent = Agent(j)
	agent.pre_train()
	return True

def learn(j):
	return agent.learn()

def predict(j):
	return agent.predict(j)

if __name__ == "__main__":
	app.run()
