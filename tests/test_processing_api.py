# flake8: noqa: E402

import sys
import os


sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app")),
)

from typing import Any
from unittest.mock import patch
from starlette.testclient import TestClient
from app.api import app
import os
import json

client = TestClient(app)

MOCK_LLM_RESPONSE = {
    "age": {
        "Description": "Age information",
        "Annotations": {
            "IsAbout": {"Label": "Age variable", "TermURL": "nb:Age"},
            "Transformation": {
                "TermURL": "nb:FromInt",
                "Label": "integer value",
            },
        },
    }
}


@patch("app.categorization.llm_categorization.llm_invocation")
def test_process_files_age(mock_llm_invocation: Any) -> None:
    # Define the behavior of the mock
    mock_llm_invocation.return_value = MOCK_LLM_RESPONSE

    # Create a temporary TSV file for testing
    file_path: str = "test_file.tsv"
    with open(file_path, "w") as f:
        f.write("age\n12")

    # Make the request
    with open(file_path, "rb") as f:
        response = client.post(
            "/process/",
            files={"file": (file_path, f, "text/tsv")},
            params={"code_system": "cogatlas"},
        )

    # Check the response
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"

    # Save the response content to a temporary file for validation
    response_file_path: str = "response.json"
    with open(response_file_path, "wb") as out_file:
        out_file.write(response.content)

    # Check that the response file exists
    assert os.path.exists(response_file_path)

    # Load and verify the content of the response file
    with open(response_file_path) as out_file:
        response_json: dict[str, Any] = json.load(out_file)

    # Check that the content matches the expected structure
    assert response_json == MOCK_LLM_RESPONSE

    # Clean up the temporary files
    os.remove(file_path)
    os.remove(response_file_path)
