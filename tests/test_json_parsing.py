import os
import json
from pathlib import Path
import pytest
from typing import Dict, Union, List

from app.parsing.json_parsing import (
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
    mapping_file: str = "app/parsing/diagnosisTerms.json"
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
    result = process_parsed_output(parsed_output, "snomed")
    assert result == expected_result


def test_diagnosis_variable(
    levels_mapping_fixture: Union[
        Dict[str, Dict[str, str]], Dict[str, List[Dict[str, str]]]
    ]
) -> None:
    parsed_output: Dict[str, Union[str, Dict[str, str], None]] = {
        "TermURL": "nb:Diagnosis",
        "Levels": {
            "PD": [
                "Indication for modification of patient cognitive status",
                "Persistent depressive disorder",
                "Presenile dementia",
                "Uncomplicated presenile dementia",
                "Paranoid disorder",
                "Psychogenic dyspepsia",
                "Prion disease",
                "Patchy dementia",
                "Pallidal degeneration",
                "Paroxysmal dystonia",
                "Mania",
                "Parkinsonism",
                "Personality disorder",
                "Panic disorder",
                "Phobic disorder",
                "Psychologic dyspareunia",
                "Panic disorder without agoraphobia with severe panic attacks",
                "Parkinson's disease",
                "Psychosexual disorder",
                "Axis II diagnosis",
                "Psychotic disorder",
                "Disorder of basal ganglia",
                "Mental disorder",
                "Primary dysthymia",
            ],
            "CTRL": ["left for user"],
            "Group": ["left for user"],
        },
    }
    expected_result = TSVAnnotations(
        Description="Group variable",
        Levels={
            "PD": [
                "Indication for modification of patient cognitive status",
                "Persistent depressive disorder",
                "Presenile dementia",
                "Uncomplicated presenile dementia",
                "Paranoid disorder",
                "Psychogenic dyspepsia",
                "Prion disease",
                "Patchy dementia",
                "Pallidal degeneration",
                "Paroxysmal dystonia",
                "Mania",
                "Parkinsonism",
                "Personality disorder",
                "Panic disorder",
                "Phobic disorder",
                "Psychologic dyspareunia",
                "Panic disorder without agoraphobia with severe panic attacks",
                "Parkinson's disease",
                "Psychosexual disorder",
                "Axis II diagnosis",
                "Psychotic disorder",
                "Disorder of basal ganglia",
                "Mental disorder",
                "Primary dysthymia",
            ],
            "CTRL": ["left for user"],
            "Group": ["left for user"],
        },
        Annotations=Annotations(
            IsAbout=IsAboutGroup(Label="Diagnosis", TermURL="nb:Diagnosis"),
            Levels={
                "PD": [
                    {
                        "TermURL": "snomed:109898005",
                        "Label": "Indication for modification of patient cognitive status",
                    },
                    {
                        "TermURL": "snomed:1153575004",
                        "Label": "Persistent depressive disorder",
                    },
                    {
                        "TermURL": "snomed:12348006",
                        "Label": "Presenile dementia",
                    },
                    {
                        "TermURL": "snomed:191451009",
                        "Label": "Uncomplicated presenile dementia",
                    },
                    {
                        "TermURL": "snomed:191667009",
                        "Label": "Paranoid disorder",
                    },
                    {
                        "TermURL": "snomed:191972002",
                        "Label": "Psychogenic dyspepsia",
                    },
                    {"TermURL": "snomed:20484008", "Label": "Prion disease"},
                    {
                        "TermURL": "snomed:230289009",
                        "Label": "Patchy dementia",
                    },
                    {
                        "TermURL": "snomed:230302004",
                        "Label": "Pallidal degeneration",
                    },
                    {
                        "TermURL": "snomed:230310003",
                        "Label": "Paroxysmal dystonia",
                    },
                    {"TermURL": "snomed:231494001", "Label": "Mania"},
                    {"TermURL": "snomed:32798002", "Label": "Parkinsonism"},
                    {
                        "TermURL": "snomed:33449004",
                        "Label": "Personality disorder",
                    },
                    {"TermURL": "snomed:371631005", "Label": "Panic disorder"},
                    {
                        "TermURL": "snomed:386810004",
                        "Label": "Phobic disorder",
                    },
                    {
                        "TermURL": "snomed:41021005",
                        "Label": "Psychologic dyspareunia",
                    },
                    {
                        "TermURL": "snomed:43150009",
                        "Label": "Panic disorder without agoraphobia with severe panic attacks",
                    },
                    {
                        "TermURL": "snomed:49049000",
                        "Label": "Parkinson's disease",
                    },
                    {
                        "TermURL": "snomed:56627002",
                        "Label": "Psychosexual disorder",
                    },
                    {
                        "TermURL": "snomed:56641006",
                        "Label": "Axis II diagnosis",
                    },
                    {
                        "TermURL": "snomed:69322001",
                        "Label": "Psychotic disorder",
                    },
                    {
                        "TermURL": "snomed:70835005",
                        "Label": "Disorder of basal ganglia",
                    },
                    {"TermURL": "snomed:74732009", "Label": "Mental disorder"},
                    {
                        "TermURL": "snomed:83176005",
                        "Label": "Primary dysthymia",
                    },
                ],
                "CTRL": [{}],
                "Group": [{}],  # noqa: E501
            },
        ),
    )
    result = process_parsed_output(parsed_output, "snomed")
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
    result = process_parsed_output(parsed_output, "snomed")
    assert result == expected_result


def test_sex_variable(
    levels_mapping_fixture: Dict[str, Dict[str, str]]
) -> None:
    parsed_output: Dict[str, Union[str, Dict[str, str], None]] = {
        "TermURL": "nb:Sex",
        "Levels": {"M": "Male", "F": "Female"},
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
    result = process_parsed_output(parsed_output, "cogatlas")
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
    result = process_parsed_output(parsed_output, "snomed")
    assert result == expected_result


def test_assessmentTool_variable(
    assessmenttool_mapping_fixture: Dict[str, Dict[str, str]]
) -> None:
    parsed_output: Dict[str, Union[str, Dict[str, str], None]] = {
        "TermURL": "nb:Assessment",
        "AssessmentTool": "wisc-r mazes",
    }
    expected_result = TSVAnnotations(
        Description="Description of Assessment Tool conducted",
        Annotations=Annotations(
            IsAbout=IsAboutAssessmentTool(
                Label="Assessment Tool", TermURL="nb:Assessment"
            ),
            IsPartOf={
                "TermURL": "cogatlas:trm_4b86c55f3d5df",
                "Label": "wisc-r mazes",
            },
        ),
    )
    result = process_parsed_output(parsed_output, "cogatlas")
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
