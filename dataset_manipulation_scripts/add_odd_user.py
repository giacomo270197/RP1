import sys, json, random
import pandas as pd

#13775,U387,C82,Alamogordo,(32.9, -105.96)
num_computers = 2228 #should be 22284
time = [0, 0] 

time_pat = 60 #every minute
abroad_citiy = [('Tokyo', '(35.689722, 139.692222)'), ('Moscow', '(55.75, 37.616667)'), ('Sao Paulo', '(-23.55, -46.633333)')]


def write_on_logs(new_log, old_file):

    if isinstance(new_log, str):
        data = new_log.split(',')
        data[0] = int(data[0])
        listOfSeries = [pd.Series(data, index=old_file.columns)]
        df2 = old_file.append(listOfSeries , ignore_index=True)

    elif isinstance(new_log, list):
        df2 = old_file
        for line in new_log:
            data = line.split(',')
            data[0] = int(data[0])
            listOfSeries = [pd.Series(data, index=old_file.columns)]
            df2 = df2.append(listOfSeries , ignore_index=True)
        
    else:
        print('tenemos un problema')
    
    df2.sort_values(by='time', inplace=True,  kind='quicksort')
    df2.to_csv('dataset_mod', sep=',', index=False, header=False)


#connecting form a computer never seen before with consistent location
def odd_computer(user, data, logs):
    computers = data[user]['computers']
    computers_clean = set(computers)

    c = 'C'+ str(random.randint(1, num_computers))
    while c in computers_clean:
        c = 'C'+ str(random.randint(1, num_computers))

    a = logs.loc[logs.computer == c]
    city = a['location'].iloc[1]
    pos = a['lat'].iloc[1] + ',' + a['lon'].iloc[1]
    new_log = str(random.randint(time[0], time[1])) +  ',' + user +  ',' + c +  ',' + city +  ',' + pos
    print('Adding: ' + new_log)
    return new_log

def odd_n_computers(user, data, logs):
    n = 10
    computers = data[user]['computers']
    computers_clean = set(computers)

    result = []
    for i in range(n):

        c = 'C'+ str(random.randint(1, num_computers))
        while c in computers_clean:
            c = 'C'+ str(random.randint(1, num_computers))

        a = logs.loc[logs.computer == c]
        city = a['location'].iloc[1]
        pos = a['lat'].iloc[1] + ',' + a['lon'].iloc[1]

        new_log = str(random.randint(time[0], time[1])) +  ',' + user +  ',' + c +  ',' + city +  ',' + pos
        print('Adding: ' + new_log)
        result.append(new_log)

    return result

#1000 log lines of connexion every 60 seconds on an exisitng user
def bot_connexion(user, data, logs):
    a = logs.loc[logs.user == user]
    c = a['computer'].iloc[1]
    city = a['location'].iloc[1]
    pos = a['lat'].iloc[1] + ',' + a['lon'].iloc[1]
    ini_time = random.randint(time[0], time[1])
    for i in range(1000):
        new_log = str(ini_time+time_pat) +  ',' + user +  ',' + c +  ',' + city +  ',' + pos
        ini_time+=time_pat
        print(new_log)

#connceting from a city outside of new mexico
def odd_abroad_city(user, data, logs):
    a = logs.loc[logs.user == user]
    c = a['computer'].iloc[1]
    f = random.randint(0, 2)
    city = abroad_citiy[f][0]
    pos = abroad_citiy[f][1]
    print('Adding location ' + city + ' to the dataset')
    new_log = str(random.randint(time[0], time[1])) +  ',' + user +  ',' + c +  ',' + city +  ',' + pos
    return new_log



if len(sys.argv) != 4:
    print('Usage:')
    print('$python3 scrip_name.py prototype logfile action')
    print('action:')
    print('a -> add a city outside new mexico')
    print('b -> add an odd computer to the user')
    print('c -> add 10 odd different computer to the user')
    print('d -> do a+b')
    print('e -> do a+c')
    print('!!!!!!!!!!!  the result will be stored in a file called: dataset_mod !!!!!!!!!!!')

else: 

    #read prototype and logs
    prototype = sys.argv[1]
    logfile = sys.argv[2]
    option = sys.argv[3]

    logs = pd.read_csv(logfile, names = ['time', 'user', 'computer', 'location', 'lat', 'lon'])
    time[0] = logs['time'].iloc[0]
    time[1] = logs['time'].iloc[-1]


    with open(prototype) as json_file:
        data = json.load(json_file)

    for user in data:
        print('Generating odd info for user: ' + user)

        if option == 'a':
            new_log = odd_abroad_city(user, data, logs)
            write_on_logs(new_log, logs)

        elif option == 'b':
            new_log = odd_computer(user, data, logs)
            write_on_logs(new_log, logs)

        elif option == 'c':
            new_log = odd_n_computers(user, data, logs)
            write_on_logs(new_log, logs)

        elif option == 'd':
            new_log = odd_abroad_city(user, data, logs)
            new_log2 = odd_computer(user, data, logs)
            write_on_logs([new_log, new_log2], logs)

        elif option == 'e':
            new_log = odd_abroad_city(user, data, logs)
            new_log2 = odd_n_computers(user, data, logs)
            write_on_logs([new_log, new_log2], logs)
        
        else:
            print('Unknown option')

#odd_computer(user, data, logs)
#bot_connexion(user, data, logs)



