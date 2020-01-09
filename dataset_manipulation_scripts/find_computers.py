import json


exts = 'abcdefghijklm'

for ext in exts:
	res = {}

	with open('splitdataseta{}'.format(ext), 'r') as file:
		for line in file:
			line = line.split(',')
			line[2] = line[2].rstrip()

			if line[2] in res:
				if not line[1] in res[line[2]]:
					res[line[2]].append(line[1])
			else:
				res.update({line[2]: [line[1]]})


	with open('result_computers_{}'.format(ext), 'w') as file_new:
		file_new.write(json.dumps(res, indent=2))
		
	print(ext)