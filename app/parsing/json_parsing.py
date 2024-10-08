from typing import Dict, Union, Optional, List, Any, Callable, Mapping
import pandas as pd
from pydantic import BaseModel, Field
import json


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


class IsAboutAssessmentTool(IsAboutBase):
    Label: str = Field(default="Assessment Tool")
    TermURL: str


class Annotations(BaseModel):  # type:ignore
    IsAbout: Union[
        IsAboutParticipant,
        IsAboutSex,
        IsAboutAge,
        IsAboutSession,
        IsAboutGroup,
        IsAboutAssessmentTool,
    ]
    Identifies: Optional[str] = None

    Levels: Optional[
        Dict[str, Union[
            List[Dict[str, str]],  # Detailed items
            List[str],             # List of strings for simpler cases
            Dict[str, str],        # Dictionary of strings for simpler cases
            Dict[str, Dict[str, str]],  # Complex nested dictionaries
            Dict[str, List[str]]   # List of strings in dictionary format
        ]]
    ] = None
    Transformation: Optional[Dict[str, str]] = None
    IsPartOf: Optional[Union[List[Dict[str, str]], Dict[str, str], str]] = None


class TSVAnnotations(BaseModel):  # type:ignore
    Description: str
    #    Levels: Optional[Union[Dict[str, str],Dict[str, List[str]]]] = None

    Levels: Optional[Union[Dict[str, str], Dict[str, List[str]]]] = None
    # Levels: Optional[Union[Dict[str,List[str]],Dict[str,str],str]]
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
    parsed_output: Dict[str, Any],
    levels_mapping: Mapping[str, List[Dict[str, str]]],
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

    if termurl == "nb:Diagnosis":
        levels = {
            key: [
                levels_mapping.get(item.strip().lower(), {})
                for item in (value if isinstance(value, list) else [value])
            ]
            for key, value in parsed_output.get("Levels", {}).items()
        }

        # Convert lists with a single item into a single dictionary if only one value exists
        for key in levels:
            if len(levels[key]) == 1:
                levels[key] = levels[key][0]

    if termurl == "nb:Sex":
        levels = {
            key: (
                levels_mapping.get(value[0].strip().lower(), {})
                if isinstance(value, list)
                else levels_mapping.get(value.strip().lower(), {})
            )
            for key, value in parsed_output.get("Levels", {}).items()
        }

    print(levels)

    annotations = Annotations(IsAbout=annotation_instance, Levels=levels)
    return TSVAnnotations(
        Description=description,
        Levels=parsed_output.get("Levels"),
        Annotations=annotations,
    )


def handle_session(parsed_output: Dict[str, Any]) -> TSVAnnotations:
    annotation_instance = IsAboutSession(TermURL=parsed_output["TermURL"])
    description = "A session ID"
    annotations = Annotations(
        IsAbout=annotation_instance, Identifies="session"
    )
    return TSVAnnotations(Description=description, Annotations=annotations)


def handle_assessmentTool(
    parsed_output: Dict[str, Union[str, List[str]]],
    assessmenttool_mapping: Mapping[str, Dict[str, str]],
) -> TSVAnnotations:
    annotation_instance = IsAboutAssessmentTool(
        TermURL=parsed_output["TermURL"]
    )
    description = "Description of Assessment Tool conducted"
    ispartof_key = parsed_output.get("AssessmentTool", "")

    if isinstance(ispartof_key, list):
        print("Multiple entries found")
        ispartof_list = []
        for key in ispartof_key:
            key = key.strip().lower()
            ispartof_item = next(
                (
                    item
                    for item in assessmenttool_mapping.values()
                    if item["Label"].strip().lower() == key
                ),
                None,
            )
            if ispartof_item:
                ispartof_list.append(ispartof_item)
        annotations = Annotations(
            IsAbout=annotation_instance,
            IsPartOf=ispartof_list if ispartof_list else None,
        )

    elif ispartof_key == "Not found":
        empty_ispartof = {"TermURL": " ", "Label": " "}
        annotations = Annotations(IsAbout=annotation_instance, IsPartOf=empty_ispartof)

    else:
        ispartof_key = ispartof_key.strip().lower()
        ispartof = next(
            (
                item
                for item in assessmenttool_mapping.values()
                if item["Label"].strip().lower() == ispartof_key
            ),
            None,
        )
        annotations = Annotations(
            IsAbout=annotation_instance, IsPartOf=ispartof
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

# noqa: E501
def load_assessmenttool_mapping(
    mapping_file: str,
) -> Mapping[str, Dict[str, str]]:
    with open(mapping_file, "r") as file:
        mappings = json.load(file)
    return {
        term_url.strip().lower(): {
            "TermURL": f"cogatlas:{term_url.strip().lower()}",
            "Label": label.strip().lower(),
        }
        for term_url, label in mappings.items()
    }


def process_parsed_output(
    parsed_output: Dict[str, Union[str, Dict[str, str], None]],
    code_system: str,
) -> Union[str, Any]:

    # Load the levels mapping from a JSON file for diagnosis
    levels_mapping_file = "app/parsing/diagnosisTerms.json"
    levels_mapping = load_levels_mapping(levels_mapping_file)

    # Load term-mapping from a JSON file for assessment tool
    if code_system == "cogatlas":
        print("Using cognitive atlas terms for assessment tool annotation.")
        assessmenttool_mapping_file = "app/parsing/toolTerms.json"
        assessmenttool_mapping = load_assessmenttool_mapping(
            assessmenttool_mapping_file
        )
    elif code_system == "snomed":
        print("Using SNOMED CT terms for assessment tool annotation.")
        assessmenttool_mapping_file = (
            "app/parsing/measurementTerms.json"
        )
        assessmenttool_mapping = load_levels_mapping(
            assessmenttool_mapping_file
        )

    termurl_to_function: Dict[str, Callable[[Dict[str, Any]], Any]] = {
        "nb:ParticipantID": handle_participant,
        "nb:Age": handle_age,
        "nb:Session": handle_session,
    }

    termurl_to_function_with_levels: Dict[
        str,
        Callable[[Dict[str, Any], Mapping[str, Dict[str, Any]]], Any],
    ] = {
        "nb:Sex": handle_categorical,
        "nb:Diagnosis": handle_categorical,
    }

    termurl_to_function_with_assessment: Dict[
        str,
        Callable[[Dict[str, Any], Mapping[str, Dict[str, str]]], Any],
    ] = {
        "nb:Assessment": handle_assessmentTool,
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
            elif term_url in termurl_to_function_with_assessment:
                handler_function_with_assessment = (
                    termurl_to_function_with_assessment[term_url]
                )
                return handler_function_with_assessment(
                    parsed_output, assessmenttool_mapping
                )
            else:
                return (
                    f"Error: No handler function found for TermURL: {term_url}"
                )
        else:
            return "Error: TermURL is missing from the parsed output"
    elif parsed_output is None:
        return "The LLM does not find any suitable entity in the current Neurobagel data model. Please be patient as we are working on increasing the LLM performance and extending the data model :)"


def update_json_file(
    data: Union[str, TSVAnnotations], filename: str, target_key: str
) -> None:
    if isinstance(data, TSVAnnotations):
        data_dict = data.model_dump(exclude_none=True)
    else:
        data_dict = {"error": data}
# noqa: E501
    try:
        with open(filename, "r") as file:
            file_data: Dict[str, Any] = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        file_data = {}
    file_data[target_key] = data_dict
    with open(filename, "w") as file:
        json.dump(file_data, file, indent=2)