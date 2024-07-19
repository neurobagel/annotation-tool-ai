from datetime import datetime
from typing import Any, Dict


def SexLevel(result_dict: Dict[str, str], key: str) -> Dict[str, Any]:
    print("test")
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

    return {"TermURL": "nb:Sex", "Levels": result}


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
