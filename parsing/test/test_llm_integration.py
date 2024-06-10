import os
import tempfile
import json
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


def test_process_parsed_output():
    # Define sample parsed outputs with different TermURL values
    parsed_output_1 = {"TermURL": "nb:ParticipantID"}
    parsed_output_2 = {"TermURL": "nb:Sex"}
    parsed_output_3 = {"TermURL": "nb:Age"}
    parsed_output_4 = {"TermURL": "unknown"}

    # Test with sample parsed outputs
    result_1 = process_parsed_output(parsed_output_1)
    assert (
        "Subject Unique Identifier" in result_1
    )  # Check if label exists in result
    assert "nb:ParticipantID" in result_1  # Check if TermURL exists in result

    result_2 = process_parsed_output(parsed_output_2)
    assert "Sex" in result_2
    assert "nb:Sex" in result_2

    result_3 = process_parsed_output(parsed_output_3)
    assert "Age" in result_3
    assert "nb:Age" in result_3

    result_4 = process_parsed_output(parsed_output_4)
    assert "Error: No annotation model found" in result_4


def test_update_json_file():
    # Create a temporary file for testing
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as temp_file:
        filename = temp_file.name

    # Define the initial content and the data to update
    initial_content = {"age_annotation": ""}

    data_to_update = {
        "Annotations": {"IsAbout": {"Label": "Age", "TermURL": "nb:Age"}},
        "additionalField1": "Some additional information",
        "additionalField2": 123,
    }
    target_key = "age_annotation"

    # Write the initial content to the temporary file
    with open(filename, "w") as file:
        json.dump(initial_content, file, indent=2)

    # Convert the data to update to a JSON string
    data_to_update_json = json.dumps(data_to_update, indent=2)

    # Call the function to update the data
    update_json_file(data_to_update_json, filename, target_key)

    # Read the content of the file after updating
    with open(filename, "r") as file:
        updated_content = json.load(file)

    # Assertions to check if the data was updated correctly
    assert target_key in updated_content
    assert updated_content[target_key] == data_to_update

    # Clean up the temporary file
    tempfile.NamedTemporaryFile().close()
