import math
import os
import random
import statistics

from core import Prototypes


class SimpleLogfile(Prototypes):

    def __del__(self):
        self.log_file.close()

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
        if obj["interval_mean"] - 3.5 * obj["interval_stdev"] < parsed[0] - sum(obj["intervals"]) < \
                obj["interval_mean"] + 3.5 * obj["interval_stdev"]:
            c_w = 100 / (4 * obj["interval_stdev"]) * abs(
                obj["interval_mean"] - (parsed[0] - sum(obj["intervals"])))
        else:
            c_w = 9999
        c_d = self.analyze_compression(obj["intervals"], "intervals")
        # print("Intervals ", target, c_w, c_d)
        c_w = round(math.log(c_w, 2), 2) if c_w >= 1 else 0
        c_d = round(math.log(c_d, 2), 2) if c_d >= 1 else 0
        return c_w, c_d

    def analyze_lists(self, prototype, parsed, target):
        obj = None
        if target == "locations":
            obj = prototype["locations_info"][parsed[3]]
            if parsed[3] not in prototype["locations"][:-1]:
                return 9999
        elif target == "computers":
            obj = prototype["computers_info"][parsed[2]]
            if parsed[2] not in prototype["computers"][:-1]:
                return 9999
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
            prot = self.generate_prototype(parsed)
            self.prototypes[parsed[1]] = prot
            return prot
