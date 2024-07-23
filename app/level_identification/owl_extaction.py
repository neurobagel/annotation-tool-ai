import json
from rdflib import Graph
import os
from fuzzywuzzy import process, fuzz
from typing import List, Dict, Any, Tuple
from owlready2 import Thing, get_ontology


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


def get_term_hierarchy_position(ontology: Any, term_name: str) -> int | None:
    # Get the class corresponding to the term name
    term_class = ontology.search_one(label=term_name)
    if not term_class:
        return None

    # Calculate the depth of the term in the hierarchy
    depth = 0
    current_class = term_class
    while current_class.is_a and current_class.is_a[0] != Thing:
        depth += 1
        current_class = current_class.is_a[0]

    return depth


def find_highest_position_terms(
    possible_terms: Dict[str, List[str]]
) -> Dict[str, Any]:
    ontology_path: str = "app/level_identification/src/doid.owl"
    ontology: Any = get_ontology(ontology_path).load()

    # Initialize a dictionary to store the highest position term
    highest_position_terms: Dict[str, Tuple[str, int]] = {}

    for key, labels in possible_terms.items():
        # Initialize variables to track the highest position term and its depth
        highest_position: int | None = None
        best_label: str | None = None

        for label in labels:
            if label != "Not found":
                # Get the hierarchy position of the current label
                hierarchy_position: int | None = get_term_hierarchy_position(
                    ontology, label.lower()
                )

                if hierarchy_position is not None:
                    # Check if this is the highest position so far
                    if (
                        highest_position is None
                        or hierarchy_position < highest_position
                    ):
                        highest_position = hierarchy_position
                        best_label = label
                else:
                    print(f"The term '{label}' was not found in the ontology.")
            else:
                print(f"The abbreviation '{key}' did not match any labels.")

        # Store the term with the highest position
        if best_label is not None:
            highest_position_terms[key] = (best_label, highest_position)  # type: ignore # noqa: E501
        else:
            highest_position_terms[key] = ("Not found", None)  # type: ignore

    highest_position_terms = {
        key: term for key, (term, _) in highest_position_terms.items()  # type: ignore # noqa: E501
    }

    return {"Levels": highest_position_terms}


def find_full_labels(lookup_dict: Dict[str, Any]) -> Dict[str, List[str]]:

    json_file_path: str = "rag_documents/abbreviations_diagnosisTerms.json"
    with open(json_file_path, "r") as file:
        abbreviation_list: List[Dict[str, Any]] = json.load(file)

    result: Dict[str, List[str]] = {}
    for key in lookup_dict:
        labels: List[str] = []
        for item in abbreviation_list:
            if key in item["abbreviations"]:
                labels.append(item["label"])
        result[key] = labels if labels else ["Not found"]

    return result


def find_fuzzy_matches(
    all_classes: List[str], labels_dict: Dict[str, List[str]], threshold: int
) -> Dict[str, List[Tuple[str, int]]]:

    # Dictionary to store the matching results
    match_results: Dict[str, List[Tuple[str, int]]] = {}

    for key, labels in labels_dict.items():
        match_results[key] = []
        for label in labels:
            if label != "Not found":
                # Perform fuzzy matching
                matches = process.extractBests(
                    label,
                    all_classes,
                    scorer=fuzz.partial_ratio,
                    score_cutoff=threshold,
                )

                # Store matches that meet or exceed the threshold
                for match, score in matches:
                    if score >= threshold:
                        match_results[key].append((match, score))

    return match_results
