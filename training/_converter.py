import json
from collections import OrderedDict
import copy
import numpy as np

Features = OrderedDict([
    ("Id",None),
    ("Type",None),
    ("ScreenPrinter/PositionX",None),
    ("ScreenPrinter/PositionY",None),
    ("PasteInspection/PosX1",None),
    ("PasteInspection/PosY1",None),
    ("PasteInspection/PosX2",None),
    ("PasteInspection/PosY2",None),
    ("PasteInspection/PosX3",None),
    ("PasteInspection/PosY3",None),
    ("PasteInspection/PosX4",None),
    ("PasteInspection/PosY4",None),
    ("PasteInspection/PosX5",None),
    ("PasteInspection/PosY5",None),
    ("PasteInspection/PosX6",None),
    ("PasteInspection/PosY6",None),
    ("PickAndPlace/MarkerX1",None),
    ("PickAndPlace/MarkerY1",None),
    ("PickAndPlace/MarkerX2",None),
    ("PickAndPlace/MarkerY2",None),
    ("AOI1/PosX1",None),
    ("AOI1/PosY1",None),
    ("AOI1/PosX2",None),
    ("AOI1/PosY2",None),
    ("AOI1/PosX3",None),
    ("AOI1/PosY3",None),
    ("AOI1/PosX4",None),
    ("AOI1/PosY4",None),
    ("AOI1/PosX5",None),
    ("AOI1/PosY5",None),
    ("AOI1/PosX6",None),
    ("AOI1/PosY6",None),
    ("Owen1/Temp1",None),
    ("Owen2/Temp2",None),
    ("Owen3/Temp3",None),
    ("AOI2/PosX1",None),
    ("AOI2/PosY1",None),
    ("AOI2/PosX2",None),
    ("AOI2/PosY2",None),
    ("AOI2/PosX3",None),
    ("AOI2/PosY3",None),
    ("AOI2/PosX4",None),
    ("AOI2/PosY4",None),
    ("AOI2/PosX5",None),
    ("AOI2/PosY5",None),
    ("AOI2/PosX6",None),
    ("AOI2/PosY6",None),
    ("Housing/HScrew",None),
    ("ConAssembly1or2/Con1or2Screw",None),
    ("PtAssembly1/Pt1Screw1",None),
    ("PtAssembly1/Pt1Screw2",None),
    ("PtAssembly2or3/Pt2or3",None),
    ("Welding/WeldFrequency",None),
    ("Label",None)
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