import json
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


def get_assessment_label(key: str) -> Union[str, List[str]]:
    def load_dictionary(file_path: str) -> Any:
        with open(file_path, "r") as file:
            return json.load(file)

    def get_label_for_abbreviation(
        abbreviation: str, abbreviation_to_label: List[Dict[str, Any]]
    ) -> Union[str, List[str]]:
        matches = []
        for item in abbreviation_to_label:
            if abbreviation in item["abbreviations"]:
                matches.append(item["label"])
        if matches:
            return matches
        if abbreviation.isdigit():
            return "some score"
        else:
            return "LLMcheck"

    file_path = "rag_documents/abbreviations_ToolTerms.json"
    data = load_dictionary(file_path)
    result = get_label_for_abbreviation(key, data)
    print(result)
    return result
