import json


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