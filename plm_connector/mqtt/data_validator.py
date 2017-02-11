import json

dict = {}
data = {}

with open("data.txt") as f:
	for line in f:
		j = json.loads(line)	
		line = line.strip('\n')
		bn = j['bn']
		#e = j['e'][0]
		#if e['n'] == 'Source/ProdType':
		#	print(e['sv'])
		#	dict[e['sv']]
		if bn in dict:
			dict[bn]+=1
			data[bn].append(line+',')
		else:
			dict[bn]=0
			data[bn]=[line+',']
		if dict[bn]>=52:
			print(bn, dict[bn])
			print(data[bn])
			print('\n\n')

for k,v in dict.items():
	print(k,v)
