import statistics
import json
import os
import argparse
import random
import math


class Parser:

    def parse(self, line):
        line = line.split(",")
        line[-1] = line[-1].replace("\n", "")
        line[0] = int(line[0])
        return line


class Prototypes:

    def __init__(self, imp=False):
        self.prototypes = {}
        self.log_file = open("results", "w")
        self.export_file = None
        if imp:
            self.import_prototypes()

    def __del__(self):
        self.log_file.close()

    def export_prototypes(self):
        self.export_file = open("exported_prototypes", "w")
        json.dump(self.prototypes, self.export_file)
        self.export_file.close()

    def import_prototypes(self):
        self.export_file = open("exported_prototypes", "w")
        self.prototypes = json.load(self.export_file)
        self.export_file.close()

    def interval_update(self, prototype, interval):
        if len(prototype["intervals"]):
            prototype["intervals"].append(interval - sum(prototype["intervals"]))
            prototype["interval_mean"] = statistics.mean(prototype["intervals"][-100:])
            prototype["interval_stdev"] = statistics.stdev(prototype["intervals"][-100:])
        else:
            prototype["intervals"].append(interval)
            prototype["interval_mean"] = statistics.mean(2 * prototype["intervals"])
            prototype["interval_stdev"] = statistics.stdev(2 * prototype["intervals"])

    def location_update(self, prototype, location, interval):
        prototype["locations"].append(location)
        if location in prototype["locations_info"]:
            prototype["locations_info"][location]["intervals"].append(
                interval - sum(prototype["locations_info"][location]["intervals"]))
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
            prototype["computers_info"][computer]["intervals"].append(
                interval - sum(prototype["computers_info"][computer]["intervals"]))
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

    def file_compress(self, string, name=""):
        filename = "tmp_file{}".format(name)
        file = open(filename, "w")
        file.write(string)
        file.close()
        os.system("lzma -z {}".format(filename))
        new_size = os.stat("{}.lzma".format(filename)).st_size
        os.remove("{}.lzma".format(filename))
        return new_size

    def analyze_compression(self, string, kind):
        if kind == "lists":
            samples = list(set(string))
            random_string = [random.choice(samples) for _ in range(len(string))]
            random_size = self.file_compress(",".join(random_string))
            actual_size = self.file_compress(",".join(string))
        elif kind == "intervals":
            low_bound = min(string)
            high_bound = max(string)
            random_string = [random.randint(low_bound, high_bound) for _ in range(len(string))]
            random_size = self.file_compress(",".join([str(x) for x in random_string]))
            actual_size = self.file_compress(",".join([str(x) for x in string]))
        else:
            return 0
        return (100 / random_size) * actual_size

    def analyze_intervals(self, prototype, parsed, target="global"):
        obj = None
        if target == "global":
            obj = prototype
        elif target == "locations":
            obj = prototype["locations_info"][parsed[3]]
        elif target == "computers":
            obj = prototype["computers_info"][parsed[2]]
        if not obj:
            exit()
        if len(obj["intervals"]) < 100:
            return 0, 0
        # Considering 2 stdev as limit of possible lottery
        if obj["interval_mean"] - 4 * obj["interval_stdev"] < parsed[0] - sum(obj["intervals"]) < \
                obj["interval_mean"] + 4 * obj["interval_stdev"]:
            c_w = 100 / (4 * obj["interval_stdev"]) * abs(
                obj["interval_mean"] - (parsed[0] - sum(obj["intervals"])))
        else:
            c_w = 99
        c_d = self.analyze_compression(obj["intervals"], "intervals")
        # print("Intervals ", target, c_w, c_d)
        c_w = round(math.log(c_w, 2), 2) if c_w >= 1 else 0
        c_d = round(math.log(c_d, 2), 2) if c_d >= 1 else 0
        return c_w, c_d

    def analyze_lists(self, prototype, parsed, target):
        obj = None
        if target == "locations":
            obj = prototype["locations_info"][parsed[3]]
        elif target == "computers":
            obj = prototype["computers_info"][parsed[2]]
        if not obj:
            exit()
        if len(obj["intervals"]) < 100:
            return 0, 0
        frequency = (100 / len(prototype["intervals"])) * len(obj["intervals"])
        c_w = 100 - frequency
        c_d = self.analyze_compression(prototype[target][-100:], "lists")
        c_w = round(math.log(c_w, 2), 2) if c_w >= 1 else 0
        c_d = round(math.log(c_d, 2), 2) if c_d >= 1 else 0
        return c_w, c_d

    def analyze(self, prototype, parsed):
        results = [self.analyze_intervals(prototype, parsed),
                   self.analyze_intervals(prototype, parsed, target="locations"),
                   self.analyze_intervals(prototype, parsed, target="computers"),
                   self.analyze_lists(prototype, parsed, "locations"),
                   self.analyze_lists(prototype, parsed, "computers")]
        complexities = [sum(x) for x in zip(*results)]
        c_w = round(complexities[0], 2)
        c_d = round(complexities[1], 2)
        if c_w - c_d > 0:
            self.log_file.write("{}  --->\t".format(",".join([str(x) for x in parsed])))
            self.log_file.write("Cw: {}, ".format(str(c_w)))
            self.log_file.write("Cd: {}, ".format(str(c_d)))
            self.log_file.write("U: {}\n".format(str(c_w - c_d)))

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

    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run analysis program on a log file')
    parser.add_argument("filename", help="Source log file")
    parser.add_argument("-e", "--export_prototypes", action="store_true", help="Export models to file")
    parser.add_argument("-i", "--import_prototypes", action="store_true", help="Import models from file")
    args = parser.parse_args()

    # Open log file
    filename = args.filename
    file = open(filename, 'r')

    # Create a log file parser
    parser = Parser()

    # Create a collection of prototypes
    if args.import_prototypes:
        prototypes = Prototypes(imp=True)
    else:
        prototypes = Prototypes()

    # Analyze the file
    for line in file:
        analyze(line, parser, prototypes)

    # Export prototypes to file
    if args.export_prototypes:
        prototypes.export_prototypes()

    # Call prototypes destructor (For closing file handles)
    del prototypes
