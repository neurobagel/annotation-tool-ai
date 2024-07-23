import json
from rdflib import Graph
import os
from fuzzywuzzy import process, fuzz
from typing import List, Dict, Any


def extract_subclasses(
    ontology_path: str, specific_entities: List[str]
) -> List[Dict[str, Any]]:
    # Load the ontology
    g: Graph = Graph()
    g.parse(ontology_path)

    # Build the SPARQL query
    entity_filters: str = " || ".join(
        [f"?superClass = <{entity}>" for entity in specific_entities]
    )
    query: str = f"""
    SELECT ?subClass ?subClassLabel ?superClass ?superClassLabel
    WHERE {{
        ?subClass rdfs:subClassOf ?superClass .
        OPTIONAL {{ ?subClass rdfs:label ?subClassLabel . }}
        OPTIONAL {{ ?superClass rdfs:label ?superClassLabel . }}
        FILTER ({entity_filters})
    }}
    """

    results = g.query(query)

    # Create a dictionary to store subclasses per superclass
    subclasses_dict: Dict[str, List[Dict[str, Any]]] = {}

    # Process the results
    for row in results:
        subClass, subClassLabel, superClass, superClassLabel = row
        subClassLabel = subClassLabel if subClassLabel else str(subClass)
        superClassLabel = (
            superClassLabel if superClassLabel else str(superClass)
        )
        superclass_name: str = str(superClassLabel).replace(" ", "_")

        if superclass_name not in subclasses_dict:
            subclasses_dict[superclass_name] = []

        # Add subclass as a dictionary with 'label' and 'TermURL'
        subclasses_dict[superclass_name].append(
            {"label": str(subClassLabel), "TermURL": str(subClass)}
        )

    # Write subclasses to separate files
    output_dir = "app/level_identification/src"
    os.makedirs(output_dir, exist_ok=True)

    for superClass, subclasses in subclasses_dict.items():
        filename = os.path.join(output_dir, f"{superClass}.txt")
        with open(filename, "w") as file:
            for entry in subclasses:
                label = entry["label"]
                termURL = entry["TermURL"]
                file.write(f"{label},{termURL}\n")

    # Flatten the subclasses_dict into a list of dictionaries
    flattened_list = [
        entry for sublist in subclasses_dict.values() for entry in sublist
    ]

    return flattened_list


def match_label_with_abbreviations(
    label: str, abbreviation_list: List[Dict[str, Any]], threshold: int
) -> List[Dict[str, Any]]:

    # Extract labels from the abbreviation list
    labels = [item["label"] for item in abbreviation_list]

    # Use fuzzy matching to find all labels above the threshold
    matches = process.extractBests(
        label, labels, scorer=fuzz.partial_ratio, score_cutoff=threshold
    )

    matched_entries = []

    # Collect the matched labels and their abbreviations
    for match_label, _ in matches:
        for item in abbreviation_list:
            if item["label"] == match_label:
                matched_entries.append(
                    {
                        "label": match_label,
                        "abbreviations": item["abbreviations"],
                    }
                )

    return matched_entries


def check_abbreviations_in_levels_tsv(
    levels_tsv: Dict[str, str],
    subclass_list: List[Dict[str, Any]],
    abbreviation_list: List[Dict[str, Any]],
) -> Dict[str, List[str]]:

    matched_keys: Dict[str, List[str]] = {key: [] for key in levels_tsv.keys()}

    for subclass in subclass_list:
        label = subclass["label"]
        matches = match_label_with_abbreviations(label, abbreviation_list, 60)
        print(matches)
        for match in matches:
            for abbreviation in match["abbreviations"]:
                if abbreviation in levels_tsv:
                    matched_keys[abbreviation].append(label)

    return matched_keys


def main() -> None:
    ontology_path = "app/level_identification/src/doid.owl"
    specific_entities = [
        "http://purl.obolibrary.org/obo/DOID_150",  # mental disorder
        "http://purl.obolibrary.org/obo/DOID_863",  # nervous system
    ]
    levels_tsv = {"HC": "", "PDD": ""}  # testing purposes

    subclass_dict = extract_subclasses(ontology_path, specific_entities)
    # print(subclass_dict)

    # Abbreviation list
    json_file_path = "rag_documents/abbreviations_diagnosisTerms.json"
    with open(json_file_path, "r") as file:
        abbreviation_list = json.load(file)

    matched_keys = check_abbreviations_in_levels_tsv(
        levels_tsv, subclass_dict, abbreviation_list
    )

    print("Matched Keys and Labels:")
    for key, labels in matched_keys.items():
        print(f"{key}: {labels}")


if __name__ == "__main__":
    main()
