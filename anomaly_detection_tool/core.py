import sys
import statistics
import json
import os
import lzma


class Parser:

    def parse(self, line):
        line = line.split(",")
        line[-1] = line[-1].replace("\n", "")
        line[0] = int(line[0])
        return line


class Prototypes:

    def __init__(self):
        self.prototypes = {}
        self.log_file = open("results", "w")

    def __del__(self):
        self.log_file.close()

    def interval_update(self, prototype, interval):
        if len(prototype["intervals"]):
            prototype["intervals"].append(interval - prototype["intervals"][-1])
            prototype["interval_mean"] = statistics.mean(prototype["intervals"][-100:])
            prototype["interval_stdev"] = statistics.stdev(prototype["intervals"][-100:])
        else:
            prototype["intervals"].append(interval)
            prototype["interval_mean"] = statistics.mean(2 * prototype["intervals"])
            prototype["interval_stdev"] = statistics.stdev(2 * prototype["intervals"])

    def location_update(self, prototype, location, interval):
        prototype["locations"].append(location)
        if location in prototype["locations_info"]:
            prototype["locations_info"][location]["intervals"].append(interval)
            prototype["locations_info"][location]["interval_mean"] = statistics.mean(
                prototype["locations_info"][location]["intervals"][-100:])
            prototype["locations_info"][location]["interval_stdev"] = statistics.stdev(
                prototype["locations_info"][location]["intervals"][-100:])
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
                prototype["computers_info"][computer]["intervals"][-100:])
            prototype["computers_info"][computer]["interval_stdev"] = statistics.stdev(
                prototype["computers_info"][computer]["intervals"][-100:])
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

    def file_compress(self, string, name):
        filename = "tmp_file{}".format(name)
        file = open(filename, "w")
        file.write(string)
        file.close()
        initial_size = os.stat("tmp_file{}".format(name)).st_size
        os.system("lzma -z {}".format(filename))
        new_size = os.stat("{}.lzma".format(filename)).st_size
        os.remove("{}.lzma".format(filename))
        return (100 / initial_size) * new_size

    def analyze_global_intervals(self, prototype, parsed):
        if len(prototype["intervals"]) < 100:
            return 0, 0
        # Considering 2 stdev as limit of possible lottery
        if prototype["interval_mean"] - prototype["interval_stdev"] < parsed[0] < prototype[
            "interval_mean"] + prototype["interval_stdev"]:
            c_w = 100 / prototype["interval_stdev"] * abs(
                prototype["interval_mean"] - (parsed[0] - prototype["intervals"][-1]))
        else:
            c_w = 9999999
        c_d = self.file_compress(",".join([str(x) for x in prototype["intervals"][-100:]]), "intervals")
        return c_w, c_d

    def analyze(self, prototype, parsed):
        x, y = self.analyze_global_intervals(prototype, parsed)
        self.log_file.write("Cw: {}, ".format(str(x)))
        self.log_file.write("Cd: {}, ".format(str(y)))
        self.log_file.write("U: {}\n".format(str(x - y)))

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
    prototypes.analyze(prototype, parsed)

if __name__ == "__main__":
    filename = sys.argv[1]
    file = open(filename, 'r')
    parser = Parser()
    prototypes = Prototypes()
    for line in file:
        analyze(line, parser, prototypes)
    del prototypes
