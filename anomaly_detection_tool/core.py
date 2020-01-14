import json
from simple_logfile import SimpleLogfile


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

    def assign_to_prototype(self, parsed):
        raise NotImplemented("Must implement this class!")

    def update(self, prototype, parsed):
        raise NotImplemented("Must implement this class!")

    def analyze(self, prototype, parsed):
        raise NotImplemented("Must implement this class!")

    def export_prototypes(self):
        self.export_file = open("exported_prototypes", "w")
        json.dump(self.prototypes, self.export_file)
        self.export_file.close()

    def import_prototypes(self):
        self.export_file = open("exported_prototypes", "r")
        self.prototypes = json.load(self.export_file)
        self.export_file.close()


def analyze(line, parser, prototypes):
    parsed = parser.parse(line)
    prototype = prototypes.assign_to_prototype(parsed)
    prototypes.update(prototype, parsed)
    prototypes.analyze(prototype, parsed)


def main(filename, logtype, export_prototypes, import_prototypes):
    # Open log file
    file = open(filename, 'r')

    # Create a log file parser
    parser = Parser()

    # Create a collection of prototypes

    choices = {
        "simple": SimpleLogfile,
    }

    if logtype not in choices:
        raise exit("Must choose a valid log class")

    if import_prototypes:
        prototypes = choices[logtype](imp=True)
    else:
        prototypes = choices[logtype]()

    # Analyze the file
    for line in file:
        analyze(line, parser, prototypes)

    # Export prototypes to file
    if export_prototypes:
        prototypes.export_prototypes()

    # Call prototypes destructor (For closing file handles)
    del prototypes
