from typing import Dict, Union, Optional, List, Any
import pandas as pd
import json
from pydantic import BaseModel, Field


class IsAboutBase(BaseModel):  # type: ignore
    Label: str
    TermURL: str


class IsAboutParticipant(IsAboutBase):
    Label: str = Field(default="Subject Unique Identifier")
    TermURL: str


class IsAboutSession(IsAboutBase):
    Label: str = Field(default="Run Identifier")
    TermURL: str


class IsAboutSex(IsAboutBase):
    Label: str = Field(default="Sex")
    TermURL: str


class IsAboutAge(IsAboutBase):
    Label: str = Field(default="Age")
    TermURL: str


class Annotations(BaseModel):  # type: ignore
    IsAbout: Union[IsAboutParticipant, IsAboutSex, IsAboutAge, IsAboutSession]
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


def handle_sex(parsed_output: Dict[str, Any]) -> TSVAnnotations:
    annotation_instance = IsAboutSex(TermURL=parsed_output["TermURL"])
    description = "Sex variable"
    levels_mapping = {
        "male": {"TermURL": "snomed:248153007", "Label": "Male"},
        "female": {"TermURL": "snomed:248152002", "Label": "Female"},
    }
    levels = {
        key: {
            "TermURL": levels_mapping[value.strip().lower()]["TermURL"],
            "Label": levels_mapping[value.strip().lower()]["Label"],
        }
        for key, value in parsed_output.get("Levels", {}).items()
        if value.strip().lower() in levels_mapping
    }
    annotations = Annotations(IsAbout=annotation_instance, Levels=levels)
    return TSVAnnotations(
        Description=description,
        Levels={k: v["Label"] for k, v in levels.items()},
        Annotations=annotations,
    )


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


def handle_session(parsed_output: Dict[str, Any]) -> TSVAnnotations:
    annotation_instance = IsAboutSession(TermURL=parsed_output["TermURL"])
    description = "A session ID"
    annotations = Annotations(
        IsAbout=annotation_instance, Identifies="session"
    )
    return TSVAnnotations(Description=description, Annotations=annotations)


def process_parsed_output(
    parsed_output: Union[
        str, Dict[str, Union[str, Dict[str, str], None]], None
    ]
) -> Union[str, TSVAnnotations]:
    termurl_to_model = {
        "nb:ParticipantID": handle_participant,
        "nb:Sex": handle_sex,
        "nb:Age": handle_age,
        "nb:Session": handle_session,
    }

    if isinstance(parsed_output, dict):
        term_url = parsed_output.get("TermURL")
        if isinstance(term_url, str) and term_url in termurl_to_model:
            handler_function = termurl_to_model[term_url]
            return handler_function(parsed_output)
        else:
            return (
                f"Error: No handler function found for TermURL: {term_url}"
                if term_url
                else "Error: TermURL is missing from the parsed output"
            )
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

    # LLM-Categorization magic

    # Create output for each column
    for key, value in columns_dict.items():
        print(key, value)
        # parsed_output = chain.invoke({"column": key, "content": value})
        # print(parsed_output)
        parsed_output: Dict[str, Union[str, Dict[str, str], None]] = {
            "TermURL": "nb:Sex",
            "Levels": {"M": "male", "F": "female"},
        }
        # parsed_output = {"TermURL": "nb:ParticipantID"}
        # parsed_output = {"TermURL": "nb:Age", \
        #                  "Format":"europeanDecimalValue"}
        # parsed_output = {"TermURL": "nb:Session"}
        print(type(parsed_output))
        result = process_parsed_output(parsed_output)
        print(result)
        print(type(result))
        update_json_file(result, "output.json", key)
