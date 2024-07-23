import json
from collections import defaultdict

def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def preprocess_data(data):
    abbreviation_to_labels = defaultdict(list)
    for entry in data:
        label = entry['label']
        for abbreviation in entry['abbreviations']:
            abbreviation_to_labels[abbreviation].append(label)
    return abbreviation_to_labels

def save_dictionary(dictionary, file_path):
    with open(file_path, 'w') as file:
        json.dump(dictionary, file)

# Path to your JSON file
file_path = 'Docfolder/abbreviations_ToolTerms.json'

# Load the JSON data
data = load_json(file_path)

# Preprocess data to create a dictionary for fast lookups
abbreviation_to_labels = preprocess_data(data)

# Save the dictionary to a file
dictionary_file_path = 'Docfolder/abbreviation_to_labels.json'
save_dictionary(abbreviation_to_labels, dictionary_file_path)
