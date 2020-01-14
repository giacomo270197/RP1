from simple_logfile import SimpleLogfile


class Parser:

    def parse(self, line):
        line = line.split(",")
        line[-1] = line[-1].replace("\n", "")
        line[0] = int(line[0])
        return line


def analyze(line, parser, prototypes):
    parsed = parser.parse(line)
    prototype = prototypes.assign_to_prototype(parsed)
    prototypes.analyze(prototype, parsed)
    prototypes.update(prototype, parsed)


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
