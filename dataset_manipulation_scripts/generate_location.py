import json
import random
import sys

cities = {
    'Albuquerque': (35.084, -106.651),
    'Las Cruces': (32.312, -106.778),
    'Rio Rancho': (35.233, -106.664),
    'Enchanted Hills': (35.337, -106.593),
    'Santa Fe': (35.687, -105.938),
    'Roswell': (33.394, -104.525),
    'Farmington': (36.728, -108.219),
    'South Valley': (35.01, -106.678),
    'Clovis': (34.405, -103.205),
    'Hobbs': (32.703, -103.136),
    'Alamogordo': (32.9, -105.96),
    'Carlsbad': (32.421, -104.229)
}

with open("result_computers", "r") as f_1:
    computers = json.load(f_1)

with open("result_users", "r") as f_2:
    users = json.load(f_2)

computers_locations = {}
users_locations = {}

with open(sys.argv[1], "r") as file:
    with open(sys.argv[2], "w") as write_file:
        for line in file:
            line = line.split(",")
            line[2] = line[2].replace('\n', '')
            if len(computers[line[2]]) > 1:
                if line[2] in computers_locations:
                    line.append(computers_locations[line[2]])
                    line.append(cities[computers_locations[line[2]]])
                else:
                    computers_locations.update({line[2]: list(cities.keys())[random.randint(0, len(cities)-1)]})
                    line.append(computers_locations[line[2]])
                    line.append(cities[computers_locations[line[2]]])
            else:
                city = list(cities.keys())[random.randint(0, len(cities)-1)]
                coordinates = cities[city]
                line.append(city)
                line.append(coordinates)
            line = [str(x) for x in line]
            write_file.write(",".join(line))
            write_file.write("\n")
