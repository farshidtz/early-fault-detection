import json
from collections import OrderedDict
import copy
import numpy as np

Features = OrderedDict([
    ("Id",""),
    ("Type", ""),
    ("ScreenPrinter/PositionX",0),
    ("ScreenPrinter/PositionY",0),
    ("PasteInspection/PosX1",0),
    ("PasteInspection/PosY1",0),
    ("PasteInspection/PosX2",0),
    ("PasteInspection/PosY2",0),
    ("PasteInspection/PosX3",0),
    ("PasteInspection/PosY3",0),
    ("PasteInspection/PosX4",0),
    ("PasteInspection/PosY4",0),
    ("PasteInspection/PosX5",0),
    ("PasteInspection/PosY5",0),
    ("PasteInspection/PosX6",0),
    ("PasteInspection/PosY6",0),
    ("PickAndPlace/MarkerX1",0),
    ("PickAndPlace/MarkerY1",0),
    ("PickAndPlace/MarkerX2",0),
    ("PickAndPlace/MarkerY2",0),
    ("AOI1/PosX1",0),
    ("AOI1/PosY1",0),
    ("AOI1/PosX2",0),
    ("AOI1/PosY2",0),
    ("AOI1/PosX3",0),
    ("AOI1/PosY3",0),
    ("AOI1/PosX4",0),
    ("AOI1/PosY4",0),
    ("AOI1/PosX5",0),
    ("AOI1/PosY5",0),
    ("AOI1/PosX6",0),
    ("AOI1/PosY6",0),
    ("Owen1/Temp1",0),
    ("Owen2/Temp2",0),
    ("Owen3/Temp3",0),
    ("AOI2/PosX1",0),
    ("AOI2/PosY1",0),
    ("AOI2/PosX2",0),
    ("AOI2/PosY2",0),
    ("AOI2/PosX3",0),
    ("AOI2/PosY3",0),
    ("AOI2/PosX4",0),
    ("AOI2/PosY4",0),
    ("AOI2/PosX5",0),
    ("AOI2/PosY5",0),
    ("AOI2/PosX6",0),
    ("AOI2/PosY6",0),
    ("Housing/HScrew",0),
    ("ConAssembly1or2/Con1or2Screw",0),
    ("PtAssembly1/Pt1Screw1",0),
    ("PtAssembly1/Pt1Screw2",0),
    ("PtAssembly2or3/Pt2or3",0),
    ("Welding/WeldFrequency",0),
    ("Label", False)
])


""" converts ResultValue of json OGC-SensorThings to python OrderedDict """
def SensorThings2Dict(json_string):
	features = copy.deepcopy(Features)
	j = json.loads(json_string)
	total = j['ResultValue']['total']
	if total != 51:
		raise Exception("Total not 51.")
	#type = j['ResultValue']['type']['e'][0]['sv']
	#label = j['ResultValue']['label']['e'][0]['bv']
	#name = j['ResultValue']['label']['bn']
	measurements = j['ResultValue']['measurements']['e']
	features["Id"] = j['ResultValue']['label']['bn']
	features["Type"] = j['ResultValue']['type']['e'][0]['sv']
	features["Label"] = j['ResultValue']['label']['e'][0]['bv']
	for entry in measurements:
		#print('("{}",0),'.format(entry['n']))
		feature_name = entry['n']
		# parallel stations
		if feature_name == "ConAssembly1/Con1Screw" or feature_name == "ConAssembly2/Con2Screw":
			feature_name = "ConAssembly1or2/Con1or2Screw"
		elif feature_name == "PtAssembly2/Pt2" or feature_name == "PtAssembly3/Pt2":
			feature_name = "PtAssembly2or3/Pt2or3"
		
		features[feature_name] = entry['v']
	
	return features