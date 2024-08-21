import sys
import os

# Add the app directory to sys.path
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app"))
)

from typing import Any, Generator  # noqa: E402
from unittest.mock import MagicMock, patch  # noqa: E402
import pytest  # noqa: E402
from app.categorization.llm_categorization import (  # noqa: E402
    AssessmentTool,
    # Diagnosis,
    llm_invocation,
)
from app.categorization.llm_helper import (  # noqa: E402
    AgeFormat,
    SexLevel,
    get_assessment_label,
)


@pytest.fixture  # type: ignore
def mock_llm_response() -> Generator[Any, Any, Any]:
    with patch(
        "app.categorization.llm_categorization.ChatOllama"
    ) as MockChatOllama:
        instance = MockChatOllama.return_value
        instance.invoke = MagicMock()
        yield instance.invoke


def test_llm_invocation_sex(mock_llm_response: Any) -> None:
    result_dict = {"pheno_sex": "pheno_sex m f o"}
    mock_llm_response.return_value = "Sex"

    with patch(
        "app.categorization.promptTemplate.PromptTemplate"
    ) as MockPromptTemplate:
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = "Sex"
        MockPromptTemplate.return_value.__or__.return_value = mock_chain

        with patch(
            "app.categorization.llm_categorization.GeneralPrompt",
            new=MagicMock(),
        ) as MockGeneralPrompt:
            MockGeneralPrompt.__or__.return_value = mock_chain
            output = llm_invocation(result_dict, "snomed")
            expected_output = {
                "TermURL": "nb:Sex",
                "Levels": {"m": "male", "f": "female", "o": "other"},
            }
            assert output == expected_output


def test_llm_invocation_participant(mock_llm_response: Any) -> None:
    result_dict = {"participant_id": "sub-01 sub-02 sub-03"}
    mock_llm_response.return_value = "Participant_IDs"

    with patch(
        "app.categorization.promptTemplate.PromptTemplate"
    ) as MockPromptTemplate:
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = "Participant_IDs"
        MockPromptTemplate.return_value.__or__.return_value = mock_chain

        with patch(
            "app.categorization.llm_categorization.GeneralPrompt",
            new=MagicMock(),
        ) as MockGeneralPrompt:
            MockGeneralPrompt.__or__.return_value = mock_chain
            output = llm_invocation(result_dict, "cogatlas")
            expected_output = {"TermURL": "nb:ParticipantID"}
            assert output == expected_output


def test_llm_invocation_session(mock_llm_response: Any) -> None:
    result_dict = {"session_id": "ses-01 ses-02"}
    mock_llm_response.return_value = "Session_IDs"

    with patch(
        "app.categorization.promptTemplate.PromptTemplate"
    ) as MockPromptTemplate:
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = "Session_IDs"
        MockPromptTemplate.return_value.__or__.return_value = mock_chain

        with patch(
            "app.categorization.llm_categorization.GeneralPrompt",
            new=MagicMock(),
        ) as MockGeneralPrompt:
            MockGeneralPrompt.__or__.return_value = mock_chain
            output = llm_invocation(result_dict, "snomed")
            expected_output = {"TermURL": "nb:Session"}
            assert output == expected_output


def test_llm_invocation_age(mock_llm_response: Any) -> None:
    result_dict = {"pheno_age": "34.1 35.3 NA"}
    mock_llm_response.return_value = "Age"

    with patch(
        "app.categorization.promptTemplate.PromptTemplate"
    ) as MockPromptTemplate:
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = "Age"
        MockPromptTemplate.return_value.__or__.return_value = mock_chain

        with patch(
            "app.categorization.llm_categorization.GeneralPrompt",
            new=MagicMock(),
        ) as MockGeneralPrompt:
            MockGeneralPrompt.__or__.return_value = mock_chain
            output = llm_invocation(result_dict, "snomed")
            expected_output = {"TermURL": "nb:Age", "Format": "floatvalue"}
            assert output == expected_output



def test_llm_invocation_diagnosis(mock_llm_response: Any) -> None:
    key = "diagnosis"
    value = "diagnosis PD PD HC HC PD"
    mock_llm_response.return_value = "yes"

    with patch(
        "app.categorization.promptTemplate.PromptTemplate"
    ) as MockPromptTemplate:
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = "yes"
        MockPromptTemplate.return_value.__or__.return_value = mock_chain

        with patch(
            "app.categorization.llm_categorization.DiagnosisPrompt",
            new=MagicMock(),
        ) as DiagnosisPrompt:
            DiagnosisPrompt.__or__.return_value = mock_chain
            output = Diagnosis(key, value, "snomed")
            expected_output = {
    'TermURL': 'nb:Diagnosis',
    'Levels': {
        'PD': [
            'Indication for modification of patient cognitive status',
            'Persistent depressive disorder',
            'Presenile dementia',
            'Uncomplicated presenile dementia',
            'Paranoid disorder',
            'Psychogenic dyspepsia',
            'Prion disease',
            'Patchy dementia',
            'Pallidal degeneration',
            'Paroxysmal dystonia',
            'Mania',
            'Parkinsonism',
            'Personality disorder',
            'Panic disorder',
            'Phobic disorder',
            'Psychologic dyspareunia',
            'Panic disorder without agoraphobia with severe panic attacks',
            "Parkinson's disease",
            'Psychosexual disorder',
            'Axis II diagnosis',
            'Psychotic disorder',
            'Disorder of basal ganglia',
            'Mental disorder',
            'Primary dysthymia'
        ],
        'HC': [
            'Healthy Control',
            'Hemichorea',
            'Hemicephaly',
            'Hydrocephalus',
            'Hepatitis with hepatic coma',
            "Huntington's chorea",
            'Hypomyelination and congenital cataract',
            'Hepatic coma',
            "Henoch's chorea"
        ]
    }
}

            assert output == expected_output


def test_llm_invocation_assessment_cogatlas(mock_llm_response: Any) -> None:
    key = "bdi"
    value = "bdi 10 18 17 13 6 3 2 7"
    mock_llm_response.return_value = "yes"
    code_system = "cogatlas"

    with patch(
        "app.categorization.promptTemplate.PromptTemplate"
    ) as MockPromptTemplate:
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = "yes"
        MockPromptTemplate.return_value.__or__.return_value = mock_chain

        with patch(
            "app.categorization.llm_categorization.AssessmentToolPrompt",
            new=MagicMock(),
        ) as DiagnosisPrompt:
            DiagnosisPrompt.__or__.return_value = mock_chain
            output = AssessmentTool(key, value, code_system)
            expected_output = {
                "TermURL": "nb:Assessment",
                "AssessmentTool": "battelle developmental inventory",
            }
            assert output == expected_output


def test_llm_invocation_assessment_snomed(mock_llm_response: Any) -> None:
    key = "bdi"
    value = "bdi 10 18 17 13 6 3 2 7"
    mock_llm_response.return_value = "yes"
    code_system = "snomed"

    with patch(
        "app.categorization.promptTemplate.PromptTemplate"
    ) as MockPromptTemplate:
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = "yes"
        MockPromptTemplate.return_value.__or__.return_value = mock_chain

        with patch(
            "app.categorization.llm_categorization.AssessmentToolPrompt",
            new=MagicMock(),
        ) as DiagnosisPrompt:
            DiagnosisPrompt.__or__.return_value = mock_chain
            output = AssessmentTool(key, value, code_system)
            expected_output = {
                "TermURL": "nb:Assessment",
                "AssessmentTool": "Beck depression inventory",
            }
            assert output == expected_output


def test_sex_level() -> None:
    result_dict = {"sex": "sex male female m M O f F"}
    output = SexLevel(result_dict, "sex")
    expected_output = {
        "TermURL": "nb:Sex",
        "Levels": {
            "male": "male",
            "female": "female",
            "m": "male",
            "M": "male",
            "O": "other",
            "f": "female",
            "F": "female",
        },
    }
    assert output == expected_output



def test_age_format() -> None:
    result_dict = {"age": "34 35.3 NA"}
    output = AgeFormat(result_dict, "age")
    expected_output = {"TermURL": "nb:Age", "Format": "integervalue"}
    assert output == expected_output


def test_get_assessment_label() -> None:
    # perfect match
    assert get_assessment_label("BDI", "snomed") == [
        "Beck depression inventory"
    ]
    # partial match
    assert get_assessment_label("BDI_Score", "cogatlas") == [
        "battelle developmental inventory"
    ]
    assert get_assessment_label("Item1_BDI", "snomed") == [
        "Beck depression inventory"
    ]
    # no match
    assert (
        get_assessment_label("handedness", "snomed")
        == "Cannot evaluate column header: no match found."
    )