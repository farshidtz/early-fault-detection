import json
import copy

STATEMENT_MASTER_FILE = 'statement_master.json'
product_types = ["ABU1", "ABU2", "ABU3", "ABU4", "ABU5", "ABU6"]

with open(STATEMENT_MASTER_FILE) as data_file:
    print "Loading " + STATEMENT_MASTER_FILE
    statement_master = json.load(data_file)

# build and export statement object files
bootstrapping = []
for x in product_types:
    statement = copy.deepcopy(statement_master)
    with open(x+"_layout.json") as statement_data_file:
        print "Loading " + x+"_layout.json"
        layout = json.load(statement_data_file)
        statement["Model"]["Parameters"]["Classifier"]["production_layout"] = layout
        statement["Name"] = layout["type"]
        with open('generated_'+x+'.json', 'w') as outfile:
            print 'Saving generated_'+x+'.json'
            json.dump(statement, outfile, indent=2, sort_keys=True)
        bootstrapping.append(statement)

# build and export bootstrapping file
with open('generated_bootstrapping.json', 'w') as outfile:
    print 'Saving generated_bootstrapping.json'
    json.dump(bootstrapping, outfile, indent=2, sort_keys=True)
