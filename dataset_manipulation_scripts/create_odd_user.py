import sys, json, random
import pandas as pd


new_user = 11363
change_user = 'U665' 
time = [0, 0] 
freq = 3000 # 50 minuts
changed_location = 'Rio Rancho'

#change user intervals and made them regular
def change_user(user, data, logs):
	a = logs.loc[logs.user == user]
	logs = logs[logs.user != user]

	ini_time = time[0] + random.randint(0, 100)
	print('Doing intervals of ' + str(ini_time))

	for index, row in a.iterrows():
		a.at[index, 'time'] = str(ini_time)
		ini_time = ini_time + freq
		
	df3 = logs.append(a, ignore_index=True)
	df3.sort_values(by='time', inplace=True,  kind='quicksort')
	print(df3.head(100))
	df3.to_csv('dataset_mod2', sep=',', index=False, header=False)
	

#make connexions from one location (Rio Ancho at the moment)
def change_location_freq(user, data, logs):
	a = logs.loc[(logs.user == user) & (logs.location == changed_location)]
	logs = logs[(logs.user != user) & (logs.location != changed_location)]

	ini_time = time[0] + random.randint(0, 100)
	print('Doing intervals of ' + str(ini_time) + ' for ' + changed_location + ' connexion')

	for index, row in a.iterrows():
		a.at[index, 'time'] = str(ini_time)
		ini_time = ini_time + freq

	df3 = logs.append(a, ignore_index=True)
	df3.sort_values(by='time', inplace=True,  kind='quicksort')
	print(df3.head(100))
	df3.to_csv('dataset_mod2', sep=',', index=False, header=False)





if len(sys.argv) != 3:
    print('Usage:')
    print('$python3 scrip_name.py prototype logfile')
    print('!!!!!!!!!!!  the result will be stored in a file called: dataset_mod2 !!!!!!!!!!!')

else: 

	prototype = sys.argv[1]
	logfile = sys.argv[2]


	logs = pd.read_csv(logfile, names = ['time', 'user', 'computer', 'location', 'lat', 'lon'])
	time[0] = logs['time'].iloc[0]
	time[1] = logs['time'].iloc[-1]

	with open(prototype) as json_file:
	    data = json.load(json_file)

	for user in data:
		print('Modifing user: ' + user)
		change_user(user, data, logs)
