from flask import Flask, request
import json

app = Flask(__name__)
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

""" HANDLERS """
@app.route("/build", methods=["POST"])
def build_handler():
	return json.dumps(build(request.json))

@app.route("/train", methods=["POST"])
def train_handler():
	return json.dumps(train(request.json))

@app.route("/predict", methods=["POST"])
def predict_handler():
	return json.dumps(predict(request.json))

def build(j):
	print(j)
	return {"built": "ack"}

def train(j):
	print(j)
	return {"train": "ack"}

def predict(j):
	print(j)
	#return {"predict": "prediction"}
	return j

if __name__ == "__main__":
	app.run()
