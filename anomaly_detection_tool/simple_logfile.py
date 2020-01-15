import math
import os
import random
import statistics

from prototypes import Prototypes


class SimpleLogfile(Prototypes):

    def __del__(self):
        self.log_file.close()

    def fast_mean(self, mean, length, new_value):
        return (new_value + (mean * length)) / (length + 1)

    def fast_stdev(self, stdev, old_mean, new_mean, length, new_value):
        return math.sqrt(
            ((stdev * stdev * (length - 2)) + (new_value - new_mean) * (new_value - old_mean)) / (length - 1)
        )

    def lg(self, x):
        return x

    def interval_update(self, prototype, parsed, target="global"):

        interval = parsed[0]
        obj = None

        # Update intervals for global user
        if target == "global":
            if len(prototype["intervals"]) <= 0:
                prototype["intervals"] += [0, interval]
                prototype["interval_mean"] = interval / 2
                prototype["interval_stdev"] = 0
                return
            obj = prototype

        # Update intervals for location
        elif target == "locations":
            if parsed[3] not in prototype["locations_info"]:
                prototype["locations"].append(parsed[3])
                prototype["locations_info"][parsed[3]] = {
                    "interval_mean": interval,
                    "interval_stdev": 0,
                    "intervals": [0, interval]
                }
                return
            obj = prototype["locations_info"][parsed[3]]

        # Update intervals for computers
        elif target == "computers":
            if parsed[2] not in prototype["computers_info"]:
                prototype["computers"].append(parsed[2])
                prototype["computers_info"][parsed[2]] = {
                    "interval_mean": interval,
                    "interval_stdev": 0,
                    "intervals": [0, interval]
                }
                return
            obj = prototype["computers_info"][parsed[2]]

        if not obj:
            exit("No object")

        if len(obj["intervals"]):
            obj["interval_mean"] = statistics.mean(obj["intervals"][-1000:])
            obj["interval_stdev"] = statistics.stdev(obj["intervals"][-1000:])
            obj["intervals"].append(interval - sum(obj["intervals"]))

    def update(self, prototype, parsed):
        self.interval_update(prototype, parsed, "global")
        self.interval_update(prototype, parsed, "locations")
        self.interval_update(prototype, parsed, "computers")

    def file_compress(self, string, name=""):
        filename = "tmp_file{}".format(name)
        file = open(filename, "w")
        file.write(string)
        file.close()
        os.system("lzma -z {}".format(filename))
        new_size = os.stat("{}.lzma".format(filename)).st_size
        os.remove("{}.lzma".format(filename))
        return new_size

    def analyze_compression(self, string, kind, mean=0, stdev=0):
        if kind == "lists":
            samples = list(set(string))
            random_string = [random.choice(samples) for _ in range(len(string))]
            same_string = [samples[0] for _ in range(len(string))]
            random_size = self.file_compress(",".join(random_string))
            same_size = self.file_compress(",".join(same_string))
            actual_size = self.file_compress(",".join(string))
        elif kind == "intervals":
            random_string = [random.uniform(mean - stdev, mean + stdev) for _ in range(len(string))]
            same_string = [mean for _ in range(len(string))]
            random_size = self.file_compress(",".join([str(x) for x in random_string]))
            same_size = self.file_compress(",".join([str(x) for x in same_string]))
            actual_size = self.file_compress(",".join([str(x) for x in string]))
        else:
            return 0
        if random_size == same_size:
            return 0
        if actual_size < same_size:
            actual_size = same_size
        return (100 / (random_size - same_size)) * (actual_size - same_size)

    def analyze_intervals(self, prototype, parsed, target="global"):
        obj = None
        if target == "global":
            obj = prototype
        elif target == "locations":
            if parsed[3] not in prototype["locations"]:
                return 9999, 0
            obj = prototype["locations_info"][parsed[3]]
        elif target == "computers":
            if parsed[2] not in prototype["computers"]:
                return 9999, 0
            obj = prototype["computers_info"][parsed[2]]
        if not obj:
            exit()
        if len(obj["intervals"]) < 100:
            return 0, 0
        # Considering n stdev as limit of possible lottery
        if obj["interval_mean"] - 4 * obj["interval_stdev"] <= parsed[0] - sum(obj["intervals"]) <= \
                obj["interval_mean"] + 4 * obj["interval_stdev"]:
            if obj["interval_stdev"] == 0:
                return 0, 0
            c_w = 100 / (30 * obj["interval_stdev"]) * abs(obj["interval_mean"] - (parsed[0] - sum(obj["intervals"])))
        else:
            return 9999, 0
        c_d = self.analyze_compression(obj["intervals"][-50:], "intervals", obj["interval_mean"], obj["interval_stdev"])
        c_w = round(self.lg(c_w), 2) if c_w >= 1 else 0
        c_d = round(self.lg(c_d), 2) if c_d >= 1 else 0
        return c_w + 1, c_d

    def analyze_lists(self, prototype, parsed, target):
        obj = None
        if target == "locations":
            if parsed[3] not in prototype["locations"]:
                return 9999, 0
            obj = prototype["locations_info"][parsed[3]]
        elif target == "computers":
            if parsed[2] not in prototype["computers"]:
                return 9999, 0
            obj = prototype["computers_info"][parsed[2]]
        if not obj:
            exit()
        if len(obj["intervals"]) < 100:
            return 0, 0
        frequency = (100 / len(prototype["intervals"])) * len(obj["intervals"])
        c_w = 100 - frequency
        c_d = self.analyze_compression(prototype[target], "lists")
        c_w = round(self.lg(c_w), 2) if c_w >= 1 else 0
        c_d = round(self.lg(c_d), 2) if c_d >= 1 else 0
        return c_w, c_d

    def analyze(self, prototype, parsed):
        results = [self.analyze_intervals(prototype, parsed),
                   # self.analyze_intervals(prototype, parsed, target="locations"),
                   self.analyze_intervals(prototype, parsed, target="computers"),
                   # self.analyze_lists(prototype, parsed, "locations"),
                   self.analyze_lists(prototype, parsed, "computers")]
        for num, w in zip(range(3), results):
            x = w[0]
            y = w[1]
            if x - y >= 1:
                print(num, ": ", ",".join([str(p) for p in parsed]), "Cw: ", x, " Cd: ", y, " U: ", x - y)

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
