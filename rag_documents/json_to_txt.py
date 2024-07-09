import json
import argparse

# Read the JSON file
# Parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("--file", help="Path to the JSON file")
args = parser.parse_args()

# Read the JSON file
with open(args.file) as json_file:
    data = json.load(json_file)

# Get the input file name without extension
input_file_name = args.file.split(".")[0]

# Create the output file name by replacing the extension with '.txt'
output_file_name = f"{input_file_name}.txt"

# Open the output file to write
with open(output_file_name, "w") as file:
    # Iterate over each dictionary in the list
    for entry in data:
        # For each abbreviation, write "abbreviation: label" in lowercase
        for abbreviation in entry["abbreviations"]:
            file.write(f"{abbreviation}: {entry['label'].lower()}\n")
