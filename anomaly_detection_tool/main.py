from core import main
import argparse

# Parse command line arguments
parser = argparse.ArgumentParser(description='Run analysis program on a log file')
parser.add_argument("filename", help="Source log file")
parser.add_argument("-e", "--export_prototypes", action="store_true", help="Export models to file")
parser.add_argument("-i", "--import_prototypes", action="store_true", help="Import models from file")
args = parser.parse_args()

import_prototypes = False
export_prototypes = False

if args.export_prototypes:
    export_prototypes = True

if args.import_prototypes:
    import_prototypes = True

main(args.filename, export_prototypes, import_prototypes)
