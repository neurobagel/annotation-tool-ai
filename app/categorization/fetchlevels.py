import json
import re
from typing import Dict, Any, List, Union


def Diagnosis_Levels(entry: str) -> None:
    print("entry")

    def load_dictionary(file_path: str) -> Any:
        with open(file_path, "r") as file:
            return json.load(file)

    def get_label_for_abbreviation(
        abbreviation: str, abbreviation_to_label: Dict[str, str]
    ) -> str:
        if abbreviation in abbreviation_to_label:
            return abbreviation_to_label[abbreviation]
        elif abbreviation.isdigit():
            return "some score"
        else:
            return "LLMcheck"

    file_path = "Docfolder/abbreviation_to_labels.json"
    data = load_dictionary(file_path)
    abbreviation_to_check = entry
    result = get_label_for_abbreviation(abbreviation_to_check, data)
    print(result)


def get_assessment_label(key: str, code_system: str) -> Union[str, List[str]]:
    def load_dictionary(file_path: str) -> Any:
        with open(file_path, "r") as file:
            return json.load(file)

    def get_label_for_abbreviation(
        key: str, abbreviation_to_label: List[Dict[str, Any]]
    ) -> Union[str, List[str]]:
        matches = set()  # Use a set to handle duplicate labels
        key_lower = key.lower()

        # Split the key by separation characters and check for exact matches
        split_keys = re.split(r"[_-]", key_lower)

        for item in abbreviation_to_label:
            for abbr in item["abbreviations"]:
                abbr_lower = abbr.lower()

                # Exact match
                if abbr_lower == key_lower:
                    matches.add(item["label"])

                # Check if any part of the split key matches the abbreviation
                if any(part == abbr_lower for part in split_keys):
                    matches.add(item["label"])

                # Strict substring match with word boundaries
                if re.search(
                    r"\b{}\b".format(re.escape(abbr_lower)), key_lower
                ):
                    matches.add(item["label"])

        # Convert the set to a list before returning
        matches_list = list(matches)

        # Return results based on the matches found
        if matches_list:
            return matches_list
        elif key.isdigit():
            return "Cannot evaluate column header: it is a number."
        else:
            return "Cannot evaluate column header: no match found."

    # Determine file path based on code system
    if code_system == "cogatlas":
        file_path = "rag_documents/abbreviations_ToolTerms.json"
    elif code_system == "snomed":
        file_path = "rag_documents/abbreviations_measurementTerms.json"
    else:
        return "Invalid code system"

    data = load_dictionary(file_path)
    result = get_label_for_abbreviation(key, data)
    print(result)
    return result
