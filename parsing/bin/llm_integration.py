from typing import Dict, List, Optional, Union, Any
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
    Levels: Optional[Dict[str, str]] = Field(
        default=None, description="Levels for the sex annotation"
    )


class IsAboutAge(IsAboutBase):
    Label: str = Field(default="Age")
    TermURL: str


class Annotations(BaseModel):  # type: ignore
    IsAbout: Union[IsAboutParticipant, IsAboutSex, IsAboutAge, IsAboutSession]
    Identifies: Optional[str] = None
    Levels: Optional[Dict[str, Dict[str, str]]] = None
    Transformation: Optional[Dict[str, str]] = None

    class Config:
        # Allow extra fields
        extra = "allow"
        # Exclude fields with value None
        exclude_none = True

    def dict(
        self,
        *,
        exclude_unset: bool = True,  # Exclude fields that have not been set
        **kwargs: Union[str, int, float, bool, None],
    ) -> Dict[str, Any]:
        model_dict: Dict[str, Any] = super().dict(
            exclude_unset=exclude_unset,
            **kwargs,
        )

        # Conditionally remove Levels if it's None
        if model_dict.get("Levels") is None:
            model_dict.pop("Levels", None)

        # Conditionally remove Identifies if it's None
        if model_dict.get("Identifies") is None:
            model_dict.pop("Identifies", None)

        # Conditionally remove Transformation if it's None
        if model_dict.get("Transformation") is None:
            model_dict.pop("Transformation", None)

        return model_dict


class TSVAnnotations(BaseModel):  # type:ignore
    Description: str
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
    data = {column: "" for column in columns}
    with open(json_file, "w") as file:
        json.dump(data, file, indent=4)


def process_parsed_output(
    parsed_output: Dict[str, Union[str, Any]]
) -> Union[str, TSVAnnotations]:
    termurl_to_model: Dict[str, type[IsAboutBase]] = {
        "nb:ParticipantID": IsAboutParticipant,
        "nb:Sex": IsAboutSex,
        "nb:Age": IsAboutAge,
        "nb:Session": IsAboutSession,
    }

    levels_mapping = {
        "male": {"TermURL": "snomed:248153007", "Label": "Male"},
        "female": {"TermURL": "snomed:248152002", "Label": "Female"},
        # Add mappings for other levels as needed
    }

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
        # Add mappings for other levels as needed
    }

    term_url = parsed_output.get("TermURL")
    if isinstance(term_url, str) and term_url in termurl_to_model:
        annotation_model = termurl_to_model[term_url]
        annotation_instance = annotation_model(TermURL=term_url)

        description = ""
        identifies = None
        levels = None
        transformation = None

        if isinstance(annotation_instance, IsAboutParticipant):
            description = "A participant ID"
            identifies = "participant"
        elif isinstance(annotation_instance, IsAboutSex):
            description = "Sex information"
            levels_data = parsed_output.get("Levels")
            if levels_data:
                levels = {
                    level.strip().lower(): {
                        "TermURL": levels_mapping[level.strip().lower()][
                            "TermURL"
                        ],
                        "Label": levels_mapping[level.strip().lower()][
                            "Label"
                        ],
                    }
                    for level in levels_data
                    if level.strip().lower() in levels_mapping
                }
        elif isinstance(annotation_instance, IsAboutAge):
            description = "Age information"
            transformation_data = parsed_output.get("Format")
            if transformation_data:
                if isinstance(transformation_data, list):
                    transformation_key = transformation_data[0].strip().lower()
                else:
                    transformation_key = transformation_data.strip().lower()

                if transformation_key in transformation_mapping:
                    transformation = transformation_mapping[transformation_key]

        elif isinstance(annotation_instance, IsAboutSession):
            description = "A session ID"
            identifies = "session"

        annotations_data = {
            "IsAbout": annotation_instance,
            "Identifies": identifies,
            "Levels": levels,
            "Transformation": transformation,
        }
        annotations = Annotations(**annotations_data)

        tsv_annotations = TSVAnnotations(
            Description=description,
            Annotations=annotations,
        )

        return tsv_annotations
    else:
        return (
            f"Error: No annotation model found for TermURL: {term_url}"
            if term_url
            else "Error: TermURL is missing from the parsed output"
        )


def update_json_file(
    data: Union[str, TSVAnnotations], filename: str, target_key: str
) -> None:
    if isinstance(data, TSVAnnotations):
        data_dict = data.dict(exclude_none=True)
    else:
        data_dict = {"error": data}

    try:
        with open(filename, "r") as file:
            file_data = json.load(file)
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
        parsed_output = {"TermURL": "nb:Sex", "Levels": ["male", "female"]}
        # parsed_output ={"TermURL": "nb:ParticipantID" }
        # parsed_output = {"TermURL": "nb:Age", \
        #                   "Format":"europeanDecimalValue"}
        # parsed_output ={"TermURL": "nb:Session" }
        result = process_parsed_output(parsed_output)
        print(result)
        print(type(result))
        update_json_file(result, "output.json", key)
