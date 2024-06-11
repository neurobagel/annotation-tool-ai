import pandas as pd
from typing import Dict, List
import json
from langchain_core.pydantic_v1 import BaseModel, Field


class IsAboutParticipant(BaseModel):
    Label: str = Field(default="Subject Unique Identifier")
    TermURL: str


class IsAboutSex(BaseModel):
    Label: str = Field(default="Sex")
    TermURL: str


class IsAboutAge(BaseModel):
    Label: str = Field(default="Age")
    TermURL: str


class Annotations(BaseModel):
    IsAbout: BaseModel


class TSVAnnotations(BaseModel):
    Annotations: Annotations
    additionalField1: str
    additionalField2: int


class TermURLOutput(BaseModel):
    TermURL: str


def convert_tsv_to_dict(tsv_file: str) -> Dict[str, str]:
    # read tsv
    df = pd.read_csv(tsv_file, delimiter="\t")

    # convert each column to a string
    column_strings = {
        col: f"{col} {' '.join(df[col].astype(str).str.strip())}"
        for col in df.columns
    }

    return column_strings


def tsv_to_json(tsv_file: str, json_file: str) -> None:
    # Read the TSV file into a DataFrame
    df = pd.read_csv(tsv_file, delimiter="\t")

    # Get the column names
    columns: List[str] = df.columns.tolist()

    # Create a dictionary with column names as keys and empty strings as values
    data = {column: "" for column in columns}

    # Write the dictionary to a JSON file

    with open(json_file, "w") as file:
        json.dump(data, file, indent=4)


def process_parsed_output(parsed_output):
    termurl_to_model = {
        "nb:ParticipantID": IsAboutParticipant,
        "nb:Sex": IsAboutSex,
        "nb:Age": IsAboutAge,
    }

    if "TermURL" in parsed_output:
        term_url = parsed_output["TermURL"]
        # Select the appropriate Pydantic model based on TermURL
        if term_url in termurl_to_model:
            # Create the final annotations
            annotation_model = termurl_to_model[term_url]
            participant_annotations = TSVAnnotations(
                Annotations=Annotations(
                    IsAbout=annotation_model(TermURL=term_url)
                ),
                additionalField1="Some additional information",
                additionalField2=123,
            )

            # Return the annotated JSON
            return participant_annotations.json(indent=2)
        else:
            return f"Error: No annotation model found for TermURL: {term_url}"
    else:
        return "Error: TermURL is missing from the parsed output"


def update_json_file(data: str, filename: str, target_key: str) -> None:
    # Convert the JSON string to a dictionary
    data_dict = json.loads(data)

    try:
        with open(filename, "r") as file:
            file_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        file_data = {}

    # Update the data at the target key
    file_data[target_key] = data_dict

    # Write the updated data back to the JSON file
    with open(filename, "w") as file:
        json.dump(file_data, file, indent=2)


if __name__ == "__main__":

    file_path = "participants.tsv"

    columns_dict = convert_tsv_to_dict(file_path)
    print(columns_dict)

    headers = list(columns_dict.keys())
    print(headers)

    # create raw json file
    json_file = "output.json"
    tsv_to_json(file_path, json_file)
