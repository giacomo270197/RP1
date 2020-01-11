import sys
import json

user = sys.argv[1]
show = {}
intervals = {}

with open(sys.argv[2], "r") as file:
    for line in file:
        if user in line:
            line = line.split(",")
            line[0] = int(line[0])
            computer = line[2]
            if computer not in intervals:
                intervals[computer] = [line[0]]
            else:
                time = line[0] - intervals[computer][-1]
                intervals[computer].append(time)
                if time >= int(sys.argv[3]):
                    if computer in show:
                        show[computer].append(time)
                    else:
                        show[computer] = [time]

print(json.dumps(show, indent=2))
