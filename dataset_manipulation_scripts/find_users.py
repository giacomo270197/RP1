import json


exts = 'abcdefghijklm'

for ext in exts:
	res = {}

	with open('splitdataseta{}'.format(ext), 'r') as file:
		for line in file:
			line = line.split(',')
			line[2] = line[2].rstrip()
			if line[1] in res:
				if not line[2] in res[line[1]]:
					res[line[1]].append(line[2])
			else:
				res.update({line[1]: [line[2]]})



	with open('result_{}'.format(ext), 'w') as file_new:
		file_new.write(json.dumps(res, indent=2))
		
	print(ext)