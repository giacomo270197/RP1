import pandas as pd
import matplotlib.pyplot as plt


flights = pd.read_csv('./days/day27.cvs', names = ['time', 'user', 'computer', 'location', 'lat', 'lon'])
#print(flights.head(10))

plt.hist(flights['time'], color = 'blue', edgecolor = 'black', bins=1440)

plt.title('RP1')
plt.xlabel('Time')
plt.ylabel('Logins')
plt.show()
