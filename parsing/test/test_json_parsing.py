import os
import json
from pathlib import Path
import pytest
from typing import Dict, Union

from parsing.bin.json_parsing import (
    IsAboutAge,
    IsAboutGroup,
    IsAboutParticipant,
    Annotations,
    IsAboutSession,
    IsAboutSex,
    TSVAnnotations,
    IsAboutAssessmentTool,
    load_levels_mapping,
    convert_tsv_to_dict,
    process_parsed_output,
    update_json_file,
)


# Test for convert_tsv_to_dict function
def test_convert_tsv_to_dict() -> None:
    # Example TSV content
    sample_tsv_content = """header1\theader2\theader3
value1_1\tvalue1_2\tvalue1_3
value2_1\tvalue2_2\tvalue2_3
"""

    # Write the sample TSV content to a temporary file
    with open("sample_tsv_file.tsv", "w") as f:
        f.write(sample_tsv_content)

    # Get the path of the temporary file
    sample_tsv_file_path = os.path.abspath("sample_tsv_file.tsv")

    # Define the expected dictionary
    expected_dict = {
        "header1": "header1 value1_1 value2_1",
        "header2": "header2 value1_2 value2_2",
        "header3": "header3 value1_3 value2_3",
    }

    # Call the function with the file path
    result_dict = convert_tsv_to_dict(sample_tsv_file_path)

    # Assert that the result matches the expected dictionary
    assert result_dict == expected_dict

    # Clean up the temporary file
    os.remove(sample_tsv_file_path)


@pytest.fixture  # type: ignore
def levels_mapping_fixture() -> Dict[str, Dict[str, str]]:
    mapping_file: str = "parsing/bin/diagnosisTerms.json"
    levels_mapping: Dict[str, Dict[str, str]] = load_levels_mapping(
        mapping_file
    )
    return levels_mapping


@pytest.fixture  # type: ignore
def assessmenttool_mapping_fixture() -> Dict[str, Dict[str, str]]:
    return {
        "trm_4b86c55f3d5df": {
            "TermURL": "cogatlas:trm_4b86c55f3d5df",
            "Label": "WISC-R Mazes",
        }
    }


def test_participant_id(
    levels_mapping_fixture: Dict[str, Dict[str, str]]
) -> None:
    parsed_output: Dict[str, Union[str, Dict[str, str], None]] = {
        "TermURL": "nb:ParticipantID"
    }
    expected_result = TSVAnnotations(
        Description="A participant ID",
        Annotations=Annotations(
            IsAbout=IsAboutParticipant(
                Label="Subject Unique Identifier", TermURL="nb:ParticipantID"
            ),
            Identifies="participant",
        ),
    )
    result = process_parsed_output(parsed_output)
    assert result == expected_result


def test_diagnosis_variable(
    levels_mapping_fixture: Dict[str, Dict[str, str]]
) -> None:
    parsed_output: Dict[str, Union[str, Dict[str, str], None]] = {
        "TermURL": "nb:Diagnosis",
        "Levels": {"PD": "Parkinson's Disease", "CTRL": "Healthy Control"},
    }
    expected_result = TSVAnnotations(
        Description="Group variable",
        Levels={"PD": "Parkinson's disease", "CTRL": "Healthy Control"},
        Annotations=Annotations(
            IsAbout=IsAboutGroup(Label="Diagnosis", TermURL="nb:Diagnosis"),
            Levels={
                "PD": {
                    "TermURL": "snomed:49049000",
                    "Label": "Parkinson's disease",
                },
                "CTRL": {"TermURL": "ncit:C94342", "Label": "Healthy Control"},
            },
        ),
    )
    result = process_parsed_output(parsed_output)
    assert result == expected_result


def test_session_id(levels_mapping_fixture: Dict[str, Dict[str, str]]) -> None:
    parsed_output: Dict[str, Union[str, Dict[str, str], None]] = {
        "TermURL": "nb:Session"
    }
    expected_result = TSVAnnotations(
        Description="A session ID",
        Annotations=Annotations(
            IsAbout=IsAboutSession(
                Label="Run Identifier", TermURL="nb:Session"
            ),
            Identifies="session",
        ),
    )
    result = process_parsed_output(parsed_output)
    assert result == expected_result


def test_sex_variable(
    levels_mapping_fixture: Dict[str, Dict[str, str]]
) -> None:
    parsed_output: Dict[str, Union[str, Dict[str, str], None]] = {
        "TermURL": "nb:Sex",
        "Levels": {"M": "male", "F": "female"},
    }
    expected_result = TSVAnnotations(
        Description="Sex variable",
        Levels={"M": "Male", "F": "Female"},
        Annotations=Annotations(
            IsAbout=IsAboutSex(Label="Sex", TermURL="nb:Sex"),
            Levels={
                "M": {"TermURL": "snomed:248153007", "Label": "Male"},
                "F": {"TermURL": "snomed:248152002", "Label": "Female"},
            },
        ),
    )
    result = process_parsed_output(parsed_output)
    assert result == expected_result


def test_age_variable(
    levels_mapping_fixture: Dict[str, Dict[str, str]]
) -> None:
    parsed_output: Dict[str, Union[str, Dict[str, str], None]] = {
        "TermURL": "nb:Age",
        "Format": "europeandecimalvalue",
    }
    expected_result = TSVAnnotations(
        Description="Age information",
        Annotations=Annotations(
            IsAbout=IsAboutAge(Label="Age variable", TermURL="nb:Age"),
            Transformation={
                "TermURL": "nb:FromEuro",
                "Label": "European value decimals",
            },
        ),
    )
    result = process_parsed_output(parsed_output)
    assert result == expected_result


def test_assessmentTool_variable(
    assessmenttool_mapping_fixture: Dict[str, Dict[str, str]]
) -> None:
    parsed_output: Dict[str, Union[str, Dict[str, str], None]] = {
        "TermURL": "nb:AssessmentTool",
        "AssessmentTool": "wisc-r mazes",
    }
    expected_result = TSVAnnotations(
        Description="Description of Assessment Tool conducted",
        Annotations=Annotations(
            IsAbout=IsAboutAssessmentTool(
                Label="Assessment Tool", TermURL="nb:AssessmentTool"
            ),
            IsPartOf={
                "TermURL": "cogatlas:trm_4b86c55f3d5df",
                "Label": "wisc-r mazes",
            },
        ),
    )
    result = process_parsed_output(parsed_output)
    assert result == expected_result


def test_update_json_file_with_valid_tsv_annotations(tmp_path: Path) -> None:
    temp_file = tmp_path / "temp.json"

    # Create a mock TSVAnnotations object
    annotations = Annotations(
        IsAbout=IsAboutParticipant(TermURL="nb:ParticipantID"),
        Identifies="participant",
    )
    tsv_annotations = TSVAnnotations(
        Description="A participant ID", Annotations=annotations
    )

    # Call update_json_file with valid TSVAnnotations data
    update_json_file(tsv_annotations, str(temp_file), "participant_data")

    # Read the JSON file and assert the content
    with open(temp_file, "r") as file:
        file_data = json.load(file)

    expected_output = {
        "participant_data": {
            "Description": "A participant ID",
            "Annotations": {
                "IsAbout": {
                    "TermURL": "nb:ParticipantID",
                    "Label": "Subject Unique Identifier",
                },
                "Identifies": "participant",
            },
        }
    }

    assert "participant_data" in file_data
    assert file_data["participant_data"]["Description"] == "A participant ID"
    assert (
        file_data["participant_data"]["Annotations"]["Identifies"]
        == "participant"
    )
    assert file_data == expected_output
