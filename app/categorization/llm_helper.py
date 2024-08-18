
from datetime import datetime
import json
import re
from typing import Any, Dict, List, Union


def SexLevel(result_dict: Dict[str, str], key: str) -> Dict[str, Any]:
    print(result_dict)
    value = result_dict[key]
    values = value.split()
    values = values[1:]  # Remove the key

    # Step 3: Define the mapping rules with case sensitivity
    mapping = {
        "female": {"f", "female", "fem", "females", "F"},
        "male": {"m", "male", "males", "M"},
        "other": {"o", "other", "others", "O"},
    }

    reverse_mapping = {}
    for category, terms in mapping.items():
        for term in terms:
            reverse_mapping[term] = category

        result = {}
    for item in set(values):  # Use set to handle unique items
        category = reverse_mapping.get(item.lower(), "unknown")
        result[item] = category

    output: Dict[str, Any] = {"TermURL": "nb:Sex", "Levels": result}
    return output


def is_integer(s: str) -> bool:
    try:
        int(s)
        return True
    except ValueError:
        return False


def is_float(s: str) -> bool:
    try:
        float(s)
        return True
    except ValueError:
        return False


def is_iso8601(s: str) -> bool:
    try:
        datetime.fromisoformat(s)
        return True
    except ValueError:
        return False


def is_european_decimal(s: str) -> bool:
    s = s.strip()  # Remove leading and trailing whitespace

    if s.count(",") == 1:
        if s.index(",") > 0 and s.index(",") < len(s) - 1:
            return True

    return False


def is_bounded(s: str) -> bool:
    if "+" in s:
        return True
    else:
        return False


def is_years(s: str) -> bool:
    s.casefold()
    if "y" in s:
        return True
    else:
        return False


def AgeFormat(result_dict: Dict[str, str], key: str) -> Dict[str, Any]:
    value = result_dict[key].strip()  # Ensure no leading/trailing whitespace
    numbers_list_str = value.split()
    Age_l = [num_str.strip() for num_str in numbers_list_str]
    Fvar: str = "Unknown"

    for num_str in Age_l:
        if is_integer(num_str):
            Fvar = "integervalue"
            break
        elif is_float(num_str):
            Fvar = "floatvalue"
            break
        elif is_iso8601(num_str):
            Fvar = "iso8601"
            break
        elif is_european_decimal(num_str):
            Fvar = "europeandecimalvalue"
            break
        elif is_bounded(num_str):
            Fvar = "boundedvalue"
            break
        elif is_years(num_str):
            Fvar = "yearunit"
            break

    output: Dict[str, str] = {
        "TermURL": "nb:Age",
        "Format": Fvar,
    }
    return output




def list_terms(key, value):
    words = value.split()
    unique_entries = list(set(words))
    if key in unique_entries:
        unique_entries.remove(key)
    print("check8.0")
    print(unique_entries)
    return unique_entries



def is_score(input_string):
    # Remove all whitespace
    cleaned_string = re.sub(r'\s+', '', input_string)
    
    # Check if the string contains only digits
    if cleaned_string.isdigit():
        return True
    
    # Check if the string contains only one or two alphabetic characters with digits
    alpha_count = sum(c.isalpha() for c in cleaned_string)
    if alpha_count <= 2 and all(c.isdigit() or c.isalpha() for c in cleaned_string):
        return True
    
    return False

def are_all_digits(input_list):
    # Check if all elements in the list are digit strings
        return all(element.isdigit() for element in input_list)

def Diagnosis_Level(unique_entries:dict,code_system: str):
    # print(unique_entries)

    def load_dictionary(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)
        
   
    #get the list of related labels
    def get_label_for_abbreviation(abbreviation:str, abbreviation_to_label):
        if abbreviation in abbreviation_to_label:
            return abbreviation_to_label[abbreviation]
        elif abbreviation.isdigit():
            return ["some score"]
        else:
            return ["left for user"]
        
# Path to your JSON file
    file_path = 'app/parsing/abbreviation_to_labels.json'

# Load the JSON data
    data = load_dictionary(file_path)



    def Get_Level(unique_entries:list):
        levels = {}
        if are_all_digits(unique_entries):
            print("scores")
            levels = {str(level): "unknown" for level in unique_entries}
            print("levels only numbers")
            return levels
        else:
            for i in range (0,len(unique_entries)):
                levelfield=get_label_for_abbreviation(unique_entries[i],data)
                levels[unique_entries[i]] = levelfield
            return levels
        
    
    levels = Get_Level(unique_entries)
    print(''' 

helper return


''')
    print(levels)
    return levels

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
        file_path = "app/parsing/abbreviations_ToolTerms.json"
    elif code_system == "snomed":
        file_path = "app/parsing/abbreviations_measurementTerms.json"
    else:
        return "Invalid code system"

    data = load_dictionary(file_path)
    result = get_label_for_abbreviation(key, data)
    print(result)
    return result