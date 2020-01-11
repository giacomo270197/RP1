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


random_string = []

while len(random_string) < int(sys.argv[3]):
    random_string = random_string + [str(random.randint(0, 511))]

random_string = random_string[:int(sys.argv[3])]

patterns = []

for x in range(int(sys.argv[1])):
    pattern = []
    for _ in range(int(sys.argv[2])):
        pattern.append(str(random.randint(0, 511)))
    patterns.append(pattern)

patterns_string = []

while len(patterns_string) < int(sys.argv[3]):
    patterns_string = patterns_string + patterns[random.randint(0, len(patterns) - 1)]

patterns_string = patterns_string[:int(sys.argv[3])]

difference_random = file_compress(",".join(random_string), "random")
difference_patterns = file_compress(",".join(patterns_string), "patterns")

print("Length random string:{}\tFile size compressed random string: {}%".format(len(random_string),
                                                                                str(difference_random)))
print("Length patterns string:{}\tFile size compressed patterns string: {}%".format(len(patterns_string),
                                                                                    str(difference_patterns)))
