import os
import json
from pathlib import Path

from parsing.bin.llm_integration import (
    IsAboutParticipant,
    Annotations,
    TSVAnnotations,
)
from parsing.bin.llm_integration import (
    convert_tsv_to_dict,
    process_parsed_output,
    update_json_file,
)


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


def test_process_parsed_output() -> None:
    # Test case 1: Valid ParticipantID
    parsed_output_1 = {"TermURL": "nb:ParticipantID"}
    result_1 = process_parsed_output(parsed_output_1)
    assert isinstance(result_1, TSVAnnotations)
    assert result_1.Description == "A participant ID"
    assert result_1.Annotations.Identifies == "participant"

    # Test case 2: Valid Sex information with levels
    parsed_output_2 = {"TermURL": "nb:Sex", "Levels": ["male", "female"]}
    result_2 = process_parsed_output(parsed_output_2)
    assert isinstance(result_2, TSVAnnotations)
    assert result_2.Description == "Sex information"
    assert result_2.Annotations.Levels == {
        "male": {"TermURL": "snomed:248153007", "Label": "Male"},
        "female": {"TermURL": "snomed:248152002", "Label": "Female"},
    }

    # Test case 3: Valid Age information with transformation
    parsed_output_3 = {"TermURL": "nb:Age", "Format": "floatvalue"}
    result_3 = process_parsed_output(parsed_output_3)
    assert isinstance(result_3, TSVAnnotations)
    assert result_3.Description == "Age information"
    assert result_3.Annotations.Transformation == {
        "TermURL": "nb:FromFloat",
        "Label": "float value",
    }

    # Test case 4: Valid Session information
    parsed_output_4 = {"TermURL": "nb:Session"}
    result_4 = process_parsed_output(parsed_output_4)
    assert isinstance(result_4, TSVAnnotations)
    assert result_4.Description == "A session ID"
    assert result_4.Annotations.Identifies == "session"

    # Test case 6: Invalid TermURL
    parsed_output_6 = {"TermURL": "invalid:TermURL"}
    result_6 = process_parsed_output(parsed_output_6)
    assert (
        result_6
        == "Error: No annotation model found for TermURL: invalid:TermURL"
    )


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
