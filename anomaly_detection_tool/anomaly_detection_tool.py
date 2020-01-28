from datetime import timedelta, datetime
import json
import math
import sys
import importlib


class DarpaLogfile:

    def __init__(self, categorical_prototypes, numerical_prototypes, domain_plugin, configuration_file):
        file_categorical = open(categorical_prototypes)
        file_numerical = open(numerical_prototypes)
        
        #----------- start configurable vars --------
        with open(configuration_file) as f:
            conf_vars = json.load(f)
        self.categorical_features = conf_vars["categorical_features"]
        self.numerical_features = conf_vars["numerical_features"]
        self.focus = conf_vars["focus"]
        self.unexpectedness_allowed = conf_vars["unexpectedness_allowed"]
        #----------- end configurable vars ----------

        self.categorical_prototypes = json.load(file_categorical)
        self.numerical_prototypes = json.load(file_numerical)
        self.lookup_c_d = []
        for x in range(2**13):
            self.lookup_c_d.append(len(bin(x)[2:]))
        self.lookup = []
        for x in range(15):
            self.lookup += (2 ** x) * [x]
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

        self.time = datetime(hour=8, second=2, year=1999, day=29, month=3)
        self.domain_plugin = domain_plugin

    def parse_line(self, line):
        parsed = line.split(",")
        parsed[-1] = int(parsed[-1])
        parsed[-2] = int(parsed[-2])
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
            else:
                tmp = prototype["{}_ranking".format(name)].index(parsed[index])
                c_w = self.lookup_c_d[tmp]
                if parsed[index] not in self.observation_windows_categorical[parsed[self.focus]][name][:tmp]:
                    c_d = c_w
                else:
                    c_d = self.lookup_c_d[
                        self.observation_windows_categorical[parsed[self.focus]][name].index(parsed[index])]
            self.observation_windows_categorical[parsed[self.focus]][name].insert(0, parsed[index])
            results.append((c_w, c_d))
            if name in self.added[parsed[self.focus]] and parsed[index] in self.added[parsed[self.focus]][name]:
                self.update_categorical(prototype, parsed, name, index)
        return results

    def analyze_numerical(self, prototype, parsed):
        results = []
        for feature in self.numerical_features:
            index = feature[0]
            name = feature[1]
            parsed[index] = float(parsed[index])
            if prototype[name]["stdev"] == 0 and parsed[index] != prototype[name]["mean"]:
                threshold = 0
                c_w = self.INFINITY
            elif prototype[name]["stdev"] == 0:
                threshold = 0
                c_w = 0
            else:
                threshold = math.floor(abs(prototype[name]["mean"] - parsed[index]) / (0.25 * prototype[name]["stdev"]))
                c_w = self.lookup[threshold]
            cnt = 0
            while cnt < (threshold - 1) and self.observation_windows_numerical[parsed[self.focus]][name] and cnt < len(
                    self.observation_windows_numerical[parsed[self.focus]][name]):
                tmp = math.floor(
                    self.observation_windows_numerical[parsed[self.focus]][name][cnt] - parsed[index]) / (
                              0.25 * prototype[name]["stdev"]) + cnt
                if tmp < threshold:
                    threshold = int(tmp)
                cnt += 1
            c_d = self.lookup_c_d[threshold]
            self.observation_windows_numerical[parsed[self.focus]][name].insert(0, parsed[index])
            results.append((c_w, c_d + 1))
        return results

    def analyze(self, prototypes, line):
        res = []
        parsed = prototypes.parse_line(line)
        prototype_categorical, prototype_numerical = prototypes.assign_to_prototype(parsed)
        if prototype_categorical and prototype_numerical:
            res += prototypes.analyze_categorical(prototype_categorical, parsed)
            res += prototypes.analyze_numerical(prototype_numerical, parsed)
            c_w = 0
            c_d = 0
            if self.domain_plugin:
                res = self.domain_plugin.domain_analyze(res)
            for x, y in res:
                c_w += x
                c_d += y
            if c_w - c_d > self.unexpectedness_allowed:
                print((self.time + timedelta(seconds=float(parsed[1]))).isoformat(), parsed, c_w, c_d, c_w - c_d)
        else:
            print("New prototype, {}".format(parsed[self.focus]), "need manual intervention")


if __name__ == "__main__":
    #usage: program.py prototypes categorical_prototypes numerical_prototypes configuration_file [domain_plugin]
    if len(sys.argv) == 6:
        domain_plugin = importlib.import_module(sys.argv[5])
    else:
        domain_plugin = None
    prototypes = DarpaLogfile(sys.argv[2], sys.argv[3], domain_plugin, sys.argv[4])
    with open(sys.argv[1]) as file:
        for line in file:
            prototypes.analyze(prototypes, line)
