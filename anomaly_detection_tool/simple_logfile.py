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

    def lg(self, x, tol=1e-13):
        res = 0.0
        while x < 1:
            res -= 1
            x *= 2
        while x >= 2:
            res += 1
            x /= 2
        fp = 1.0
        while fp >= tol:
            fp /= 2
            x *= x
            if x >= 2:
                x /= 2
                res += fp
        return res

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
            old_mean = obj["interval_mean"]
            obj["interval_mean"] = self.fast_mean(obj["interval_mean"], len(obj["intervals"]),
                                                  interval - sum(obj["intervals"]))
            obj["interval_stdev"] = self.fast_stdev(obj["interval_stdev"], old_mean, obj["interval_mean"],
                                                    len(obj["intervals"]), interval - sum(obj["intervals"]))
            obj["intervals"].append(interval - sum(obj["intervals"]))
            # if target == "global":
            #     print("Global mean: {}".format(obj["interval_mean"]))
            #     print("Global stdev: {}".format(obj["interval_stdev"]))

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
        # Considering 4 stdev as limit of possible lottery
        if obj["interval_mean"] - 4 * obj["interval_stdev"] < parsed[0] - sum(obj["intervals"]) < \
                obj["interval_mean"] + 4 * obj["interval_stdev"]:
            c_w = 100 / (4 * obj["interval_stdev"]) * abs(
                obj["interval_mean"] - (parsed[0] - sum(obj["intervals"])))
        else:
            c_w = 9999
        c_d = self.analyze_compression(obj["intervals"], "intervals")
        # print("Intervals ", target, c_w, c_d)
        c_w = round(self.lg(c_w, 2), 2) if c_w >= 1 else 0
        c_d = round(self.lg(c_d, 2), 2) if c_d >= 1 else 0
        return c_w, c_d

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
        c_w = round(self.lg(c_w, 2), 2) if c_w >= 1 else 0
        c_d = round(self.lg(c_d, 2), 2) if c_d >= 1 else 0
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
