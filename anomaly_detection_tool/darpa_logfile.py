import datetime
import json
import math
import sys


class DarpaLogfile:

    def __init__(self, categorical_prototypes, numerical_prototypes):
        file_categorical = open(categorical_prototypes)
        file_numerical = open(numerical_prototypes)
        self.categorical_features = [[3, "destinations"], [2, "sources"]]
        self.numerical_features = [(5, "length")]
        self.categorical_prototypes = json.load(file_categorical)
        self.numerical_prototypes = json.load(file_numerical)
        self.lookup = []
        for exp in range(15):
            self.lookup = self.lookup + (2 ** exp) * [exp]
        assert len(self.categorical_prototypes) == len(self.numerical_prototypes)
        self.observation_windows_categorical = {}
        self.observation_windows_numerical = {}
        for key in self.categorical_prototypes:
            self.observation_windows_categorical[key] = {}
            for x in self.categorical_features:
                self.observation_windows_categorical[key][x[1]] = []
        for key in self.numerical_prototypes:
            self.observation_windows_numerical[key] = {}
            for x in self.numerical_features:
                self.observation_windows_numerical[key][x[1]] = []
        self.added = {x: {} for x in self.categorical_prototypes.keys()}
        self.INFINITY = 9999
        self.focus = 4
        self.time = datetime.datetime(hour=8, second=2, year=1999, day=29, month=3)

    def parse_line(self, line):
        parsed = line.split(",")
        parsed[-1] = int(parsed[-1].replace("\n", ""))
        return parsed

    def assign_to_prototype(self, parsed):
        if parsed[self.focus] in self.categorical_prototypes and parsed[self.focus] in self.numerical_prototypes:
            return self.categorical_prototypes[parsed[self.focus]], self.numerical_prototypes[parsed[self.focus]]
        else:
            return None, None

    def update_categorical(self, prototype, parsed, name, index):
        prototype[name][parsed[index]] += 1
        tmp = [(y, x) for x, y in prototype[name].items()]
        tmp.sort(reverse=True)
        prototype["{}_ranking".format(name)] = [y for _, y in tmp]

    def analyze_categorical(self, prototype, parsed):
        results = []
        for feature in self.categorical_features:
            index = feature[0]
            name = feature[1]
            # Return infinity if a new value is detected
            if parsed[index] not in prototype[name]:
                prototype[name].update({
                    parsed[index]: 1
                })
                prototype["{}_ranking".format(name)].append(parsed[index])
                if name in self.added[parsed[self.focus]]:
                    self.added[parsed[self.focus]][name].append(parsed[index])
                else:
                    self.added[parsed[self.focus]][name] = [parsed[index]]
                c_w = self.INFINITY
                c_d = 0
                print((self.time + datetime.timedelta(seconds=float(parsed[1]))).isoformat(), "New IP detected at ->",
                      parsed[index])
            else:
                tmp = prototype["{}_ranking".format(name)].index(parsed[index])
                c_w = self.lookup[tmp]
                if parsed[index] not in self.observation_windows_categorical[parsed[self.focus]][name][:tmp]:
                    c_d = c_w
                else:
                    c_d = self.lookup[
                        self.observation_windows_categorical[parsed[self.focus]][name].index(parsed[index])]
            self.observation_windows_categorical[parsed[self.focus]][name].insert(0, parsed[index])
            results.append((c_w, c_d))
            if name in self.added[parsed[self.focus]] and parsed[index] in self.added[parsed[self.focus]][name]:
                self.update_categorical(prototype, parsed, name, index)
        return results

    def analyze_numerical(self, prototype, parsed):
        results = []
        for feature in self.numerical_features:
            index = feature[0]  # parsed[index] is the length
            name = feature[1]  # parsed[index] is the length
            parsed[index] = float(parsed[index])
            if prototype["stdev"] == 0 and parsed[index] != prototype["mean"]:
                threshold = 0
                c_w = self.INFINITY
            elif prototype["stdev"] == 0:
                threshold = 0
                c_w = 0
            else:
                threshold = math.floor(abs(prototype["mean"] - parsed[index]) / (0.5 * prototype["stdev"]))
                c_w = self.lookup[threshold]
            cnt = 0
            while cnt < threshold and self.observation_windows_numerical[parsed[self.focus]][name] and cnt < len(
                    self.observation_windows_numerical[parsed[self.focus]][name]):
                tmp = math.floor(
                    self.observation_windows_numerical[parsed[self.focus]][name][cnt] - parsed[index]) / (
                              0.5 * prototype["stdev"]) + cnt
                if tmp < threshold:
                    threshold = int(tmp)
                cnt += 1
            c_d = self.lookup[threshold]
            self.observation_windows_numerical[parsed[self.focus]][name].insert(0, parsed[index])
            results.append((c_w, c_d))
        return results

    def analyze(self, prototypes, line):
        parsed = prototypes.parse_line(line)
        prototype_categorical, prototype_numerical = prototypes.assign_to_prototype(parsed)
        if prototype_categorical and prototype_numerical:
            res = prototypes.analyze_categorical(prototype_categorical, parsed)
            if res[0][0] - res[0][1] > 4:
                print((self.time + datetime.timedelta(seconds=float(parsed[1]))).isoformat(), parsed[-2], "Src:",
                      parsed[2], res[0][0], res[0][1], res[0][0] - res[0][1])
            if res[1][0] - res[1][1] > 4:
                print((self.time + datetime.timedelta(seconds=float(parsed[1]))).isoformat(), parsed[-2], "Dst:",
                      parsed[3], res[1][0], res[1][1], res[1][0] - res[1][1])
            res = prototypes.analyze_numerical(prototype_numerical, parsed)
            if res[0][0] - res[0][1] > 4:
                print((self.time + datetime.timedelta(seconds=float(parsed[1]))).isoformat(), parsed[-2], "Size:",
                      parsed[-1], res[0][0], res[0][1], res[0][0] - res[0][1])
        else:
            print("New protocol, {}".format(parsed[4]), "need manual intervention")


if __name__ == "__main__":
    prototypes = DarpaLogfile(sys.argv[2], sys.argv[3])
    with open(sys.argv[1]) as file:
        for line in file:
            prototypes.analyze(prototypes, line)
