import pandas as pd

#calculates the intervals in which user _Auser_ is login in in the NewMexico locations
def a(Auser, flights):

#citiy: [time between conexions]
    cities = {
        'Albuquerque' : [],
        'Las Cruces' : [],
        'Rio Rancho' : [],
        'Enchanted Hills' : [],
        'Santa Fe' : [],
        'Roswell' : [],
        'Farmington' : [],
        'South Valley' : [],
        'Clovis' : [],
        'Hobbs' : [],
        'Alamogordo' : [],
        'Carlsbad' : []
    }


    for loc in cities.keys():
        a = flights.loc[(flights.user == Auser)  & (flights.location == loc)]
        cities[loc] = a['time'].tolist()

    print(cities)
    for key, value in cities.items():
        res = []
        if len(value) > 1:
            x = value[1] - value[0]
            res.append(x)
            for i in range(2, len(value)):
                b = value[i]-value[i-1]
                res.append(b)
            print(key)
            print(res)
        else:
            res = [0]
            print(key)
            print(res)

#calculate the interval in which computer _Acomputer_ is being used
def b(Acomputer, flights):
    a = flights.loc[(flights.computer == Acomputer)]
    times = a['time'].tolist()
    res = []
    if len(times) > 1:
        x = times[1] - times[0]
        for i in range(2, len(times)):
            b = times[i] - times[i-1]
            res.append(b)
    else:
        res = [0]
    print(res)


#calculate the interval in which computer _Acomputer_ is being used by a user _Auser_
def c(Acomputer, Auser, flights):
    a = flights.loc[(flights.computer == Acomputer) & (flights.user == Auser)]
    times = a['time'].tolist()
    res = []
    if len(times) > 1:
        x = times[1] - times[0]
        for i in range(2, len(times)):
            b = times[i] - times[i-1]
            res.append(b)
    else:
        res = [0]
    print(res)



#calculate the interval in which a user _Auser_ login
def d(Auser, flights):
    a = flights.loc[(flights.user == Auser)]
    times = a['time'].tolist()
    res = []
    if len(times) > 1:
        x = times[1] - times[0]
        for i in range(2, len(times)):
            b = times[i] - times[i-1]
            res.append(b)
    else:
        res = [0]
    print(res)



flights = pd.read_csv('../datasets/partial_log', names = ['time', 'user', 'computer', 'location', 'lat', 'lon'])

#a('U53', flights)
#b('C1', flights)
#c('C1', 'U1', flights)
d('U553', flights)
