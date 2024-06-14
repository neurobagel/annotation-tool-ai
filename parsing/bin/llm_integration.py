from typing import Dict, Union, Optional, List, Any, Callable, Mapping
import pandas as pd
import json
from pydantic import BaseModel, Field


class IsAboutBase(BaseModel):  # type:ignore
    Label: str
    TermURL: str


class IsAboutParticipant(IsAboutBase):
    Label: str = Field(default="Subject Unique Identifier")
    TermURL: str


class IsAboutSession(IsAboutBase):
    Label: str = Field(default="Run Identifier")
    TermURL: str


class IsAboutSex(IsAboutBase):
    Label: str = Field(default="Sex variable")
    TermURL: str


class IsAboutAge(IsAboutBase):
    Label: str = Field(default="Age variable")
    TermURL: str


class IsAboutGroup(IsAboutBase):
    Label: str = Field(default="Diagnosis variable")
    TermURL: str


class Annotations(BaseModel):  # type:ignore
    IsAbout: Union[
        IsAboutParticipant,
        IsAboutSex,
        IsAboutAge,
        IsAboutSession,
        IsAboutGroup,
    ]
    Identifies: Optional[str] = None
    Levels: Optional[Dict[str, Dict[str, str]]] = None
    Transformation: Optional[Dict[str, str]] = None


class TSVAnnotations(BaseModel):  # type:ignore
    Description: str
    Levels: Optional[Dict[str, str]] = None
    Annotations: Annotations


def convert_tsv_to_dict(tsv_file: str) -> Dict[str, str]:
    df = pd.read_csv(tsv_file, delimiter="\t")
    column_strings: Dict[str, str] = {
        col: f"{col} {' '.join(df[col].astype(str).str.strip())}"
        for col in df.columns
    }
    return column_strings


def tsv_to_json(tsv_file: str, json_file: str) -> None:
    df = pd.read_csv(tsv_file, delimiter="\t")
    columns: List[str] = df.columns.tolist()
    data: Dict[str, str] = {column: "" for column in columns}
    with open(json_file, "w") as file:
        json.dump(data, file, indent=4)


def handle_participant(parsed_output: Dict[str, Any]) -> TSVAnnotations:
    annotation_instance = IsAboutParticipant(TermURL=parsed_output["TermURL"])
    description = "A participant ID"
    annotations = Annotations(
        IsAbout=annotation_instance, Identifies="participant"
    )
    return TSVAnnotations(Description=description, Annotations=annotations)


def handle_age(parsed_output: Dict[str, Any]) -> TSVAnnotations:
    annotation_instance = IsAboutAge(TermURL=parsed_output["TermURL"])
    description = "Age information"
    transformation_mapping = {
        "floatvalue": {"TermURL": "nb:FromFloat", "Label": "float value"},
        "integervalue": {"TermURL": "nb:FromInt", "Label": "integer value"},
        "europeandecimalvalue": {
            "TermURL": "nb:FromEuro",
            "Label": "European value decimals",
        },
        "boundedvalue": {
            "TermURL": "nb:FromBounded",
            "Label": "bounded value",
        },
        "iso8601": {
            "TermURL": "nb:FromISO8601",
            "Label": "period of time according to the ISO8601 standard",
        },
    }
    transformation_key = parsed_output.get("Format", "").strip().lower()
    transformation = transformation_mapping.get(transformation_key)
    annotations = Annotations(
        IsAbout=annotation_instance, Transformation=transformation
    )
    return TSVAnnotations(Description=description, Annotations=annotations)


def handle_categorical(
    parsed_output: Dict[str, Any], levels_mapping: Mapping[str, Dict[str, str]]
) -> TSVAnnotations:
    termurl = parsed_output.get("TermURL")

    if termurl == "nb:Sex":
        description = "Sex variable"
        annotation_instance = IsAboutSex(Label="Sex", TermURL=termurl)
    elif termurl == "nb:Diagnosis":
        description = "Group variable"
        annotation_instance = IsAboutGroup(Label="Diagnosis", TermURL=termurl)
    else:
        raise ValueError(f"Unhandled TermURL: {termurl}")

    levels = {
        key: levels_mapping.get(value.strip().lower(), {})
        for key, value in parsed_output.get("Levels", {}).items()
    }

    annotations = Annotations(IsAbout=annotation_instance, Levels=levels)
    return TSVAnnotations(
        Description=description,
        Levels={k: v["Label"] for k, v in levels.items() if "Label" in v},
        Annotations=annotations,
    )


def handle_session(parsed_output: Dict[str, Any]) -> TSVAnnotations:
    annotation_instance = IsAboutSession(TermURL=parsed_output["TermURL"])
    description = "A session ID"
    annotations = Annotations(
        IsAbout=annotation_instance, Identifies="session"
    )
    return TSVAnnotations(Description=description, Annotations=annotations)


def load_levels_mapping(mapping_file: str) -> Dict[str, Dict[str, str]]:
    with open(mapping_file, "r") as file:
        mappings = json.load(file)
    return {
        entry["label"]
        .strip()
        .lower(): {"TermURL": entry["identifier"], "Label": entry["label"]}
        for entry in mappings
    }


def process_parsed_output(
    parsed_output: Dict[str, Union[str, Dict[str, str], None]],
    levels_mapping: Mapping[str, Dict[str, str]],
) -> Union[str, TSVAnnotations]:
    termurl_to_function: Dict[
        str, Callable[[Dict[str, Any]], TSVAnnotations]
    ] = {
        "nb:ParticipantID": handle_participant,
        "nb:Age": handle_age,
        "nb:Session": handle_session,
    }

    termurl_to_function_with_levels: Dict[
        str,
        Callable[
            [Dict[str, Any], Mapping[str, Dict[str, str]]], TSVAnnotations
        ],
    ] = {
        "nb:Sex": handle_categorical,
        "nb:Diagnosis": handle_categorical,
    }

    if isinstance(parsed_output, dict):
        term_url = parsed_output.get("TermURL")
        if isinstance(term_url, str):
            if term_url in termurl_to_function:
                handler_function = termurl_to_function[term_url]
                return handler_function(parsed_output)
            elif term_url in termurl_to_function_with_levels:
                handler_function_with_levels = termurl_to_function_with_levels[
                    term_url
                ]
                return handler_function_with_levels(
                    parsed_output, levels_mapping
                )
            else:
                return (
                    f"Error: No handler function found for TermURL: {term_url}"
                )
        else:
            return "Error: TermURL is missing from the parsed output"
    else:
        return "Error: parsed_output is not a dictionary"


def update_json_file(
    data: Union[str, TSVAnnotations], filename: str, target_key: str
) -> None:
    if isinstance(data, TSVAnnotations):
        data_dict = data.dict(exclude_none=True)
    else:
        data_dict = {"error": data}

    try:
        with open(filename, "r") as file:
            file_data: Dict[str, Any] = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        file_data = {}
    file_data[target_key] = data_dict
    with open(filename, "w") as file:
        json.dump(file_data, file, indent=2)


if __name__ == "__main__":
    file_path = "participants.tsv"
    columns_dict = convert_tsv_to_dict(file_path)
    json_file = "output.json"
    tsv_to_json(file_path, json_file)

    # Load the levels mapping from a JSON file
    levels_mapping_file = "parsing/bin/diagnosisTerms.json"
    levels_mapping = load_levels_mapping(levels_mapping_file)

    # LLM-Categorization magic

    # Create output for each column
    for key, value in columns_dict.items():
        print(key, value)
        parsed_output: Dict[str, Union[str, Dict[str, str], None]] = {
            "TermURL": "nb:Age",
            "Format": "europeanDecimalValue",
        }
        # parsed_output: Dict[str, Union[str, Dict[str, str], None]] = {
        #    "TermURL": "nb:Sex",
        #    "Levels": {"M": "male", "F": "female"},
        # }
        # parsed_output = {"TermURL": "nb:ParticipantID"}
        # parsed_output = {"TermURL": "nb:Session"}
        # parsed_output = {
        #    "TermURL": "nb:Diagnosis",
        #    "Levels": {
        #        "MDD": "Major depressive disorder",
        #        "CTRL": "healthy control",
        #    },
        # }
        result = process_parsed_output(parsed_output, levels_mapping)
        print(result)
        update_json_file(result, "output.json", key)
