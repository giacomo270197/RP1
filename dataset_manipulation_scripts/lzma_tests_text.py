import random
import sys
import os


def file_compress(string, name):
    filename = "tmp_file{}".format(name)
    file = open(filename, "w")
    file.write(string)
    file.close()
    initial_size = os.stat("tmp_file{}".format(name)).st_size
    os.system("lzma -z {}".format(filename))
    new_size = os.stat("{}.lzma".format(filename)).st_size
    os.remove("{}.lzma".format(filename))
    return (100 / initial_size) * new_size


cities = ['Albuquerque', 'Las Cruces', 'Rio Rancho', 'Enchanted Hills', 'Santa Fe', 'Roswell', 'Farmington',
          'South Valley', 'Clovis', 'Hobbs', 'Alamogordo', 'Carlsbad']

random_string = ""

while len(random_string) < int(sys.argv[3]):
    random_string = random_string + cities[random.randint(0, len(cities) - 1)] + ","

random_string = random_string[:int(sys.argv[3])]

patterns = []

for x in range(int(sys.argv[1])):
    pattern = []
    for _ in range(int(sys.argv[2])):
        pattern.append(cities[random.randint(0, len(cities) - 1)])
    patterns.append(",".join([str(y) for y in pattern]))

patterns_string = ""

while len(patterns_string) < int(sys.argv[3]):
    patterns_string = patterns_string + patterns[random.randint(0, len(patterns) - 1)] + ","

patterns_string = patterns_string[:int(sys.argv[3])]

difference_random = file_compress(random_string, "random")
difference_patterns = file_compress(patterns_string, "patterns")

print("Length random string:{}\tFile size compressed random string: {}".format(len(random_string),
                                                                               str(difference_random)))
print("Length patterns string:{}\tFile size compressed patterns string: {}".format(len(patterns_string),
                                                                                   str(difference_patterns)))
