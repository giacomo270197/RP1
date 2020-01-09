import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

'''
flights = pd.read_csv('/sne/home/mbadiassimo/Downloads/locations_partial_log', names = ['time', 'user', 'computer', 'location', 'lat', 'lon'])

for i in range(28):
	a = flights.loc[(flights.time/86400 >= i) & (flights.time/86400 < i+1)] 
	print(a.head())
	a.to_csv('./days/day{}.cvs'.format(str(i)), header=False, index=False)

'''

def convertToHour(time):
	dt_object = datetime.fromtimestamp(time)
	return dt_object.hour


data = pd.read_csv('./days/day2.cvs', names = ['time', 'user', 'computer', 'location', 'lat', 'lon'])


data['hour'] = data.apply(lambda row: convertToHour(row.time), axis=1)
print(data.head())


plt.hist(data['hour'], color = 'blue', edgecolor = 'black', bins=24)
plt.title('RP1')
plt.xlabel('Hour')
plt.ylabel('Logins')
plt.show()