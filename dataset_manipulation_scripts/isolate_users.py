import sys
import re

users = sys.argv[2].split(",")

write_file = open("lines_extracted", "w")

with open(sys.argv[1]) as file:
    for line in file:
        for x in users:
            if re.search(r"\bU{}\b".format(str(x)), line):
                write_file.write(line)

write_file.close()
