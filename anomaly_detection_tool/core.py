import time
import os
import sys
import threading
import statistics
import json


class Parser:

    def parse(self, line):
        line = line.split(",")
        line[-1] = line[-1].replace("\n", "")
        line[0] = int(line[0])
        return line


class Prototypes:

    def __init__(self):
        self.prototypes = {}

    def interval_update(self, prototype, interval):
        if len(prototype["intervals"]):
            prototype["intervals"].append(interval - prototype["intervals"][-1])
            prototype["interval_mean"] = statistics.mean(prototype["intervals"])
            prototype["interval_stdev"] = statistics.stdev(prototype["intervals"])
        else:
            prototype["intervals"].append(interval)
            prototype["interval_mean"] = statistics.mean(2 * prototype["intervals"])
            prototype["interval_stdev"] = statistics.stdev(2 * prototype["intervals"])

    def location_update(self, prototype, location, interval):
        prototype["locations"].append(location)
        if location in prototype["locations_info"]:
            prototype["locations_info"][location]["intervals"].append(interval)
            prototype["locations_info"][location]["interval_mean"] = statistics.mean(
                prototype["locations_info"][location]["intervals"])
            prototype["locations_info"][location]["interval_stdev"] = statistics.stdev(
                prototype["locations_info"][location]["intervals"])
        else:
            prototype["locations_info"][location] = {
                "interval_mean": statistics.mean(2 * [interval]),
                "interval_stdev": statistics.stdev(2 * [interval]),
                "intervals": [interval]
            }

    def computer_update(self, prototype, computer, interval):
        prototype["computers"].append(computer)
        if computer in prototype["computers_info"]:
            prototype["computers_info"][computer]["intervals"].append(interval)
            prototype["computers_info"][computer]["interval_mean"] = statistics.mean(
                prototype["computers_info"][computer]["intervals"])
            prototype["computers_info"][computer]["interval_stdev"] = statistics.stdev(
                prototype["computers_info"][computer]["intervals"])
        else:
            prototype["computers_info"][computer] = {
                "interval_mean": statistics.mean(2 * [interval]),
                "interval_stdev": statistics.stdev(2 * [interval]),
                "intervals": [interval]
            }

    def update(self, prototype, parsed):
        self.interval_update(prototype, parsed[0])
        self.location_update(prototype, parsed[3], parsed[0])
        self.computer_update(prototype, parsed[2], parsed[0])

    def generate_prototype(self, parsed):
        return {
            "user": parsed[1],
            "interval_mean": 0,
            "interval_stdev": 0,
            "intervals": [],
            "locations_info": {},
            "locations": [],
            "computers_info": {},
            "computers": [],
        }

    def assign_to_prototype(self, parsed):
        if parsed[1] in self.prototypes:
            return self.prototypes[parsed[1]]
        else:
            prot = self.generate_prototype(parsed[1])
            self.prototypes[parsed[1]] = prot
            return prot


def analyze(line, parser, prototypes):
    parsed = parser.parse(line)
    prototype = prototypes.assign_to_prototype(parsed)
    prototypes.update(prototype, parsed)


filename = sys.argv[1]
file = open(filename, 'r')
# st_results = os.stat(filename)
# st_size = st_results[6]
# file.seek(st_size)
parser = Parser()
prototypes = Prototypes()
for line in file:
    analyze(line, parser, prototypes)
    # thread = threading.Thread(target=analyze, args=[line, parser, prototypes])
    # thread.start()
# while 1:
#     where = file.tell()
#     line = file.readline()
#     if not line:
#         time.sleep(1)
#         file.seek(where)
#     else:
#         thread = threading.Thread(target=analyze, args=[line, parser, prototypes])
#         thread.start()

print(json.dumps(prototypes.prototypes["U1"], indent=2))
