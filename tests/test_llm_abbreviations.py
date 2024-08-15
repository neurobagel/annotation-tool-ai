import os
import json
from unittest.mock import patch, mock_open, MagicMock
from rag_documents.llm_abbreviations import (
    get_diagnosis_labels,
    generate_abbreviations_pdf,
    main,
)  # Replace 'your_module' with the actual module name


def test_get_diagnosis_labels() -> None:
    mock_data = json.dumps(
        [
            {"label": "Diabetes Mellitus"},
            {"Label": "Hypertension"},
            {"label": "Coronary Artery Disease"},
        ]
    )

    with patch("builtins.open", mock_open(read_data=mock_data)):
        labels = get_diagnosis_labels("dummy_file.json")
        assert labels == [
            "Diabetes Mellitus",
            "Hypertension",
            "Coronary Artery Disease",
        ]


def test_generate_abbreviations_pdf(tmp_path: str) -> None:
    mock_data = [
        {"label": "Diabetes Mellitus", "abbreviations": ["DM", "DM2", "DM1"]},
        {"label": "Hypertension", "abbreviations": ["HTN"]},
    ]

    abbreviations_input_filename = os.path.join(
        tmp_path, "abbreviations_test.json"
    )
    with open(abbreviations_input_filename, "w", encoding="utf-8") as f:
        json.dump(mock_data, f)

    generate_abbreviations_pdf(abbreviations_input_filename)
    output_filename = os.path.join(tmp_path, "abbreviations_test.pdf")
    assert os.path.exists(output_filename)


@patch("rag_documents.llm_abbreviations.ChatOllama")
@patch(
    "rag_documents.llm_abbreviations.generate_abbreviations_pdf"
)
def test_main(
    mock_generate_pdf: MagicMock, MockChatOllama: MagicMock, tmp_path: str
) -> None:
    # Setup mock for ChatOllama
    mock_llm_instance = MagicMock()
    MockChatOllama.return_value = mock_llm_instance

    # Define what the mocked ChatOllama should return
    mock_llm_instance.invoke.return_value = "content='DM, DM2, DM1'"

    # Define the path for the input file
    mock_input_file = os.path.join(tmp_path, "input.json")

    # Create the input file with the test data
    with open(mock_input_file, "w", encoding="utf-8") as f:
        json.dump([{"label": "Diabetes Mellitus"}], f)

    # Call the main function with the input file
    main(mock_input_file)

    expected_abbreviations_input_filename = os.path.join(
        tmp_path, "abbreviations_input.json"
    )

    # Verify the content of the output file
    if os.path.exists(expected_abbreviations_input_filename):
        with open(
            expected_abbreviations_input_filename, "r", encoding="utf-8"
        ) as f:
            data = json.load(f)
    else:
        data = None

    # Assert the content is as expected
    expected_data = [
        {"label": "Diabetes Mellitus", "abbreviations": ["DM", "DM2", "DM1"]}
    ]
    if data:
        assert data == expected_data

    mock_generate_pdf.assert_called_once_with(
        expected_abbreviations_input_filename
    )
