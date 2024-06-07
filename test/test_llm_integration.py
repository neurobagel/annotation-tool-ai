import io
from llm_integration import convert_tsv_to_dict


def test_convert_tsv_to_dict() -> None:
    sample_tsv_content = """header1\theader2\theader3
    value1_1\tvalue1_2\tvalue1_3
    value2_1\tvalue2_2\tvalue2_3
    """
    sample_tsv_file = io.StringIO(sample_tsv_content)

    # Headers should be included in the string that is handed over to the LLM
    expected_dict = {
        "header1": "header1 value1_1 value2_1",
        "header2": "header2 value1_2 value2_2",
        "header3": "header3 value1_3 value2_3",
    }

    result_dict = convert_tsv_to_dict(sample_tsv_file)

    assert result_dict == expected_dict
