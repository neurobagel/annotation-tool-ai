import os
from bin.llm_integration import convert_tsv_to_dict


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
