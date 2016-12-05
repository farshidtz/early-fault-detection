import json

prefix = "bootstrap-"
with open("smtline-161117-0.05fr_1.txt") as f:
    for line in f:
		json_object = json.loads(myjson)
		senml_basename = json_obj[json_obj.keys()[0]]['bn']
		with open(prefix+".txt", "a") as myfile:
			myfile.write(json.dumps({senml_basename : line.strip('\n')}))
