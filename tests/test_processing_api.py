# flake8: noqa: E402
import pytest
import sys
import os

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app")),
)

from typing import Any, Generator
from unittest.mock import MagicMock, patch
from starlette.testclient import TestClient
from app.api import app
import os
import json

client = TestClient(app)

# MOCK_LLM_RESPONSE = {
#     "age": {
#     "Description": "Age information",
#     "Annotations": {
#       "IsAbout": {
#         "Label": "Age variable",
#         "TermURL": "nb:Age"
#       },
#       "Transformation": {
#         "TermURL": "nb:FromInt",
#         "Label": "integer value"
#       }
#     }
#   }
# }


# #@patch("app.categorization.llm_categorization.llm_invocation")
# def test_process_files_age(mock_llm_invocation: Any) -> None:
#     # Define the behavior of the mock
#     mock_llm_invocation.return_value = MOCK_LLM_RESPONSE

#     # Create a temporary TSV file for testing
#     file_path: str = "test_file.tsv"
#     with open(file_path, "w") as f:
#         f.write("age\n12")

#     # Make the request
#     with open(file_path, "rb") as f:
#         response = client.post(
#             "/process/",
#             files={"file": (file_path, f, "text/tsv")},
#             params={"code_system": "cogatlas"},
#         )

#     # Check the response
#     assert response.status_code == 200
#     assert response.headers["Content-Type"] == "application/json"

#     # Save the response content to a temporary file for validation
#     response_file_path: str = "response.json"
#     with open(response_file_path, "wb") as out_file:
#         out_file.write(response.content)

#     # Check that the response file exists
#     assert os.path.exists(response_file_path)

#     # Load and verify the content of the response file
#     with open(response_file_path) as out_file:
#         response_json: dict[str, Any] = json.load(out_file)

#     # Check that the content matches the expected structure
#     assert response_json == MOCK_LLM_RESPONSE

#     # Clean up the temporary files
#     os.remove(file_path)
#     os.remove(response_file_path)

####################################################################


@pytest.fixture  # type: ignore
def mock_llm_response() -> Generator[Any, Any, Any]:
    with patch(
        "categorization.llm_categorization.ChatOllama"
    ) as MockChatOllama:
        instance = MockChatOllama.return_value
        instance.invoke = MagicMock()
        yield instance.invoke


def test_process_files_sex(mock_llm_response: Any) -> None:
    with patch(
        "categorization.promptTemplate.PromptTemplate"
    ) as MockPromptTemplate:
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = "Sex"
        MockPromptTemplate.return_value.__or__.return_value = mock_chain

        with patch(
            "categorization.llm_categorization.GeneralPrompt",
            new=MagicMock(),
        ) as MockGeneralPrompt:
            MockGeneralPrompt.__or__.return_value = mock_chain

            # Create a temporary TSV file for testing
            file_path: str = "test_file.tsv"
            with open(file_path, "w") as f:
                f.write("pheno_sex\nm\nf\no")

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

            expected_output_sex = {
                "pheno_sex": {
                    "Description": "Sex variable",
                    "Levels": {
                        "f": "female",
                        "m": "male",
                        "o": "other",
                    },
                    "Annotations": {
                        "IsAbout": {
                            "Label": "Sex",
                            "TermURL": "nb:Sex",
                        },
                        "Levels": {
                            "f": {
                                "TermURL": "snomed:248152002",
                                "Label": "Female",
                            },
                            "m": {
                                "TermURL": "snomed:248153007",
                                "Label": "Male",
                            },
                            "o": {
                                "TermURL": "snomed:32570681000036106",
                                "Label": "Other",
                            },
                        },
                    },
                }
            }

            assert response_json == expected_output_sex

            # Clean up the temporary files
            os.remove(file_path)
            os.remove(response_file_path)


def test_process_files_age(mock_llm_response: Any) -> None:
    with patch(
        "categorization.promptTemplate.PromptTemplate"
    ) as MockPromptTemplate:
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = "Age"
        MockPromptTemplate.return_value.__or__.return_value = mock_chain

        with patch(
            "categorization.llm_categorization.GeneralPrompt",
            new=MagicMock(),
        ) as MockGeneralPrompt:
            MockGeneralPrompt.__or__.return_value = mock_chain

            # Create a temporary TSV file for testing
            file_path: str = "test_file.tsv"
            with open(file_path, "w") as f:
                f.write("age\n35\n12\n9")

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

            expected_output_sex = {
                "age": {
                    "Description": "Age information",
                    "Annotations": {
                        "IsAbout": {
                            "Label": "Age variable",
                            "TermURL": "nb:Age",
                        },
                        "Transformation": {
                            "TermURL": "nb:FromInt",
                            "Label": "integer value",
                        },
                    },
                }
            }

            print(mock_llm_response())
            print(response_json)
            assert response_json == expected_output_sex

            # Clean up the temporary files
            os.remove(file_path)
            os.remove(response_file_path)


def test_process_files_participant(mock_llm_response: Any) -> None:
    with patch(
        "categorization.promptTemplate.PromptTemplate"
    ) as MockPromptTemplate:
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = "Participant_IDs"
        MockPromptTemplate.return_value.__or__.return_value = mock_chain

        with patch(
            "categorization.llm_categorization.GeneralPrompt",
            new=MagicMock(),
        ) as MockGeneralPrompt:
            MockGeneralPrompt.__or__.return_value = mock_chain

            # Create a temporary TSV file for testing
            file_path: str = "test_file.tsv"
            with open(file_path, "w") as f:
                f.write("participant_id\nsub-01\nsub-02\nsub-03")

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

            expected_output_sex = {
                "participant_id": {
                    "Description": "A participant ID",
                    "Annotations": {
                        "IsAbout": {
                            "Label": "Subject Unique Identifier",
                            "TermURL": "nb:ParticipantID",
                        },
                        "Identifies": "participant",
                    },
                }
            }

            print(mock_llm_response())
            print(response_json)
            assert response_json == expected_output_sex

            # Clean up the temporary files
            os.remove(file_path)
            os.remove(response_file_path)


def test_process_files_session(mock_llm_response: Any) -> None:
    with patch(
        "categorization.promptTemplate.PromptTemplate"
    ) as MockPromptTemplate:
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = "Session_IDs"
        MockPromptTemplate.return_value.__or__.return_value = mock_chain

        with patch(
            "categorization.llm_categorization.GeneralPrompt",
            new=MagicMock(),
        ) as MockGeneralPrompt:
            MockGeneralPrompt.__or__.return_value = mock_chain

            # Create a temporary TSV file for testing
            file_path: str = "test_file.tsv"
            with open(file_path, "w") as f:
                f.write("ses\nses-01\nses-02\nses-03")

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

            expected_output_sex = {
                "ses": {
                    "Description": "A session ID",
                    "Annotations": {
                        "IsAbout": {
                            "Label": "Run Identifier",
                            "TermURL": "nb:Session",
                        },
                        "Identifies": "session",
                    },
                }
            }

            print(mock_llm_response())
            print(response_json)
            assert response_json == expected_output_sex

            # Clean up the temporary files
            os.remove(file_path)
            os.remove(response_file_path)


def test_process_files_assessment_cogatlas(mock_llm_response: Any) -> None:
    with patch(
        "categorization.promptTemplate.PromptTemplate"
    ) as MockPromptTemplate:
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = "yes"
        MockPromptTemplate.return_value.__or__.return_value = mock_chain

        with patch(
            "categorization.llm_categorization.AssessmentToolPrompt",
            new=MagicMock(),
        ) as MockGeneralPrompt:
            MockGeneralPrompt.__or__.return_value = mock_chain

            # Create a temporary TSV file for testing
            file_path: str = "test_file.tsv"
            with open(file_path, "w") as f:
                f.write("BDI\n18\n24\n06")

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

            expected_output_sex = {
                "BDI": {
                    "Description": "Description of Assessment Tool conducted",
                    "Annotations": {
                        "IsAbout": {
                            "Label": "Assessment Tool",
                            "TermURL": "nb:Assessment",
                        },
                        "IsPartOf": {
                            "TermURL": "cogatlas:trm_523e10cad0ce6",
                            "Label": "battelle developmental inventory",
                        },
                    },
                }
            }

            print(mock_llm_response())
            print(response_json)
            assert response_json == expected_output_sex

            # Clean up the temporary files
            os.remove(file_path)
            os.remove(response_file_path)


def test_process_files_assessment_snomed(mock_llm_response: Any) -> None:
    with patch(
        "categorization.promptTemplate.PromptTemplate"
    ) as MockPromptTemplate:
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = "yes"
        MockPromptTemplate.return_value.__or__.return_value = mock_chain

        with patch(
            "categorization.llm_categorization.AssessmentToolPrompt",
            new=MagicMock(),
        ) as MockGeneralPrompt:
            MockGeneralPrompt.__or__.return_value = mock_chain

            # Create a temporary TSV file for testing
            file_path: str = "test_file.tsv"
            with open(file_path, "w") as f:
                f.write("BDI\n18\n24\n06")

            # Make the request
            with open(file_path, "rb") as f:
                response = client.post(
                    "/process/",
                    files={"file": (file_path, f, "text/tsv")},
                    params={"code_system": "snomed"},
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

            expected_output_sex = {
                "BDI": {
                    "Description": "Description of Assessment Tool conducted",
                    "Annotations": {
                        "IsAbout": {
                            "Label": "Assessment Tool",
                            "TermURL": "nb:Assessment",
                        },
                        "IsPartOf": {
                            "TermURL": "snomed:273306008",
                            "Label": "Beck depression inventory",
                        },
                    },
                }
            }

            print(mock_llm_response())
            print(response_json)
            assert response_json == expected_output_sex

            # Clean up the temporary files
            os.remove(file_path)
            os.remove(response_file_path)


# Define mock return values for all columns
mock_return_values = {
    "pheno_sex": "Sex",
    "age": "Age",
    "participant_id": "Participant_IDs",
    "ses": "Session_IDs",
    "BDI": "yes",
}

MOCK_RESPONSES = {
    "pheno_sex": {
        "Description": "Sex variable",
        "Levels": {"f": "female", "m": "male", "o": "other"},
        "Annotations": {
            "IsAbout": {"Label": "Sex", "TermURL": "nb:Sex"},
            "Levels": {
                "f": {"TermURL": "snomed:248152002", "Label": "Female"},
                "m": {"TermURL": "snomed:248153007", "Label": "Male"},
                "o": {"TermURL": "snomed:32570681000036106", "Label": "Other"},
            },
        },
    },
    "age": {
        "Description": "Age information",
        "Annotations": {
            "IsAbout": {"Label": "Age variable", "TermURL": "nb:Age"},
            "Transformation": {
                "TermURL": "nb:FromInt",
                "Label": "integer value",
            },
        },
    },
    "ses": {
        "Description": "A session ID",
        "Annotations": {
            "IsAbout": {"Label": "Run Identifier", "TermURL": "nb:Session"},
            "Identifies": "session",
        },
    },
    "participant_id": {
        "Description": "A participant ID",
        "Annotations": {
            "IsAbout": {
                "Label": "Subject Unique Identifier",
                "TermURL": "nb:ParticipantID",
            },
            "Identifies": "participant",
        },
    },
    "BDI": {
        "Description": "Description of Assessment Tool conducted",
        "Annotations": {
            "IsAbout": {
                "Label": "Assessment Tool",
                "TermURL": "nb:Assessment",
            },
            "IsPartOf": {
                "TermURL": "cogatlas:trm_523e10cad0ce6",
                "Label": "battelle developmental inventory",
            },
        },
    },
}



def test_process_files_diagnosis(mock_llm_response: Any) -> None:
    with patch(
        "categorization.promptTemplate.PromptTemplate"
    ) as MockPromptTemplate:
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = "yes"
        MockPromptTemplate.return_value.__or__.return_value = mock_chain

        with patch(
            "categorization.llm_categorization.DiagnosisPrompt",
            new=MagicMock(),
        ) as MockGeneralPrompt:
            MockGeneralPrompt.__or__.return_value = mock_chain

            # Create a temporary TSV file for testing
            file_path: str = "test_file.tsv"
            with open(file_path, "w") as f:
                f.write("group\n0\n1\n0")

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

            expected_output_diagnosis = {
                "group": {
                    "Description": "Group variable",
                    "Levels": {
                    "0": "unknown",
                    "1": "unknown"
                    },
                    "Annotations": {
                        "IsAbout": {
                            "Label": "Diagnosis",
                            "TermURL": "nb:Diagnosis"
                        },
                        "Levels": {
                            "0": {},
                            "1": {}
                        }
                    }
                }
            }

            print(mock_llm_response())
            print(response_json)
            assert response_json == expected_output_diagnosis

            # Clean up the temporary files
            os.remove(file_path)
            os.remove(response_file_path)
