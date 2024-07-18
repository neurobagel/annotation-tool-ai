import pytest
from app.factories.annotation_factories.concrete_factory_age import AgeFactory
from app.factories.annotation_factories.concrete_factory_diagnosis import (
    DiagnosisFactory,
)
from app.products.annotations import Annotations
from app.products.is_about_age import IsAboutAge
from app.products.is_about_diagnosis import IsAboutGroup
from app.products.tsv_annotations import TSVAnnotations
from unittest.mock import patch, mock_open
import json
from app.factories.annotation_factories.concrete_factory_participant import (
    ParticipantFactory,
)
from app.products.is_about_participant import IsAboutParticipant
from app.factories.annotation_factories.concrete_factory_session import (
    SessionFactory,
)
from app.products.is_about_session import IsAboutSession
from app.factories.annotation_factories.concrete_factory_assessmentTool import (  # noqa: E501
    AssessmentToolFactory,
)
from app.factories.annotation_factories.concrete_factory_sex import SexFactory
from typing import Any, Dict

# AgeFactory tests#######


def test_create_annotation_agefloatvalue() -> None:
    factory: AgeFactory = AgeFactory()
    parsed_output: Dict[str, str] = {
        "TermURL": "nb:Age",
        "Format": "floatvalue",
    }
    result: TSVAnnotations = factory.create_annotation(parsed_output)
    expected_transformation: Dict[str, str] = {
        "TermURL": "nb:FromFloat",
        "Label": "float value",
    }
    expected_annotations: Annotations = Annotations(
        IsAbout=IsAboutAge(TermURL="nb:Age"),
        Transformation=expected_transformation,
    )
    expected_result: TSVAnnotations = TSVAnnotations(
        Description="Age information", Annotations=expected_annotations
    )
    assert result == expected_result


def test_create_annotation_ageintegervalue() -> None:
    factory: AgeFactory = AgeFactory()
    parsed_output: Dict[str, str] = {
        "TermURL": "nb:Age",
        "Format": "integervalue",
    }
    result: TSVAnnotations = factory.create_annotation(parsed_output)
    expected_transformation: Dict[str, str] = {
        "TermURL": "nb:FromInt",
        "Label": "integer value",
    }
    expected_annotations: Annotations = Annotations(
        IsAbout=IsAboutAge(TermURL="nb:Age"),
        Transformation=expected_transformation,
    )
    expected_result: TSVAnnotations = TSVAnnotations(
        Description="Age information", Annotations=expected_annotations
    )
    assert result == expected_result


# SexFactory tests##########

# Mock data to simulate the JSON file content
mock_json_diagnosis: str = json.dumps(
    [
        {"label": "Healthy Control", "identifier": "ncit:C94342"},
        {"label": "Male", "identifier": "snomed:248153007"},
        {"label": "Other", "identifier": "snomed:32570681000036106"},
        {"label": "Female", "identifier": "snomed:248152002"},
    ]
)

# Mock parsed output for testing
mock_parsed_output: Dict[str, Any] = {
    "TermURL": "nb:Sex",
    "Levels": {"m": "male", "f": "female"},
}


@pytest.fixture  # type: ignore
def factory() -> SexFactory:
    with patch("builtins.open", mock_open(read_data=mock_json_diagnosis)):
        return SexFactory(mapping_file="dummy_path.json")


def test_create_annotation_sex(factory: SexFactory) -> None:
    # Use the factory to create the actual annotation
    annotation: TSVAnnotations = factory.create_annotation(mock_parsed_output)

    # Convert actual annotation to dictionary for comparison
    annotation_dict: Dict[str, Any] = {
        "Description": annotation.Description,
        "Levels": annotation.Levels,
        "Annotations": {
            "IsAbout": {
                "Label": annotation.Annotations.IsAbout.Label,
                "TermURL": annotation.Annotations.IsAbout.TermURL,
            },
            "Levels": annotation.Annotations.Levels,
        },
    }

    # Define the expected result as a dictionary
    expected_result_dict: Dict[str, Any] = {
        "Description": "Sex variable",
        "Levels": {"m": "Male", "f": "Female"},
        "Annotations": {
            "IsAbout": {"Label": "Sex", "TermURL": "nb:Sex"},
            "Levels": {
                "m": {"TermURL": "snomed:248153007", "Label": "Male"},
                "f": {"TermURL": "snomed:248152002", "Label": "Female"},
            },
        },
    }

    # Assert that the result matches the expected result
    assert (
        annotation_dict == expected_result_dict
    ), "The created annotation should match the expected annotation"


# participantFactory tests#########


@pytest.fixture  # type: ignore
def participant_factory() -> ParticipantFactory:
    return ParticipantFactory()


def test_create_annotation_participant(
    participant_factory: ParticipantFactory,
) -> None:
    parsed_output: Dict[str, str] = {"TermURL": "nb:participantID"}
    result: TSVAnnotations = participant_factory.create_annotation(
        parsed_output
    )

    expected_annotation_instance: IsAboutParticipant = IsAboutParticipant(
        TermURL="nb:participantID"
    )
    expected_annotations: Annotations = Annotations(
        IsAbout=expected_annotation_instance, Identifies="participant"
    )
    expected_result: TSVAnnotations = TSVAnnotations(
        Description="A participant ID", Annotations=expected_annotations
    )
    assert result == expected_result


def test_create_annotation_missing_termurl_participant(
    participant_factory: ParticipantFactory,
) -> None:
    parsed_output: Dict[str, str] = {}
    with pytest.raises(KeyError):
        participant_factory.create_annotation(parsed_output)


# SessionFactory tests##############


@pytest.fixture  # type: ignore
def session_factory() -> SessionFactory:
    return SessionFactory()


def test_create_annotation_session(session_factory: SessionFactory) -> None:
    parsed_output: Dict[str, str] = {"TermURL": "nb:Session"}
    result: TSVAnnotations = session_factory.create_annotation(parsed_output)

    expected_annotation_instance: IsAboutSession = IsAboutSession(
        TermURL="nb:Session"
    )
    expected_annotations: Annotations = Annotations(
        IsAbout=expected_annotation_instance, Identifies="session"
    )
    expected_result: TSVAnnotations = TSVAnnotations(
        Description="A session ID", Annotations=expected_annotations
    )
    assert result == expected_result


def test_create_annotation_missing_termurl_session(
    session_factory: SessionFactory,
) -> None:
    parsed_output: Dict[str, str] = {}
    with pytest.raises(KeyError):
        session_factory.create_annotation(parsed_output)


# AssessmentToolFactory tests########

# Mock data for toolTerms.json
mock_json_data: str = json.dumps(
    {
        "trm_4fba85a597ca9": "delayed memory task",
        "trm_565a31fa6f444": "regulated heat stimulation",
        "trm_5667451917a34": "2-stage decision task",
        "trm_4a3fd79d09b6d": "backward masking",
        "trm_4fbd2af083332": "size match task",
        "trm_56674133b666c": "adaptive n-back task",
        "trm_4fbd2c18e1dd9": "object decision task",
    }
)


@pytest.fixture  # type: ignore
def assessment_tool_factory() -> AssessmentToolFactory:
    with patch("builtins.open", mock_open(read_data=mock_json_data)):
        return AssessmentToolFactory(mapping_file="dummy_path.json")


def test_create_annotation_assessmentTool(
    assessment_tool_factory: AssessmentToolFactory,
) -> None:
    parsed_output: Dict[str, str] = {
        "TermURL": "nb:Assessment",
        "AssessmentTool": "size match task",
    }
    result: TSVAnnotations = assessment_tool_factory.create_annotation(
        parsed_output
    )

    result_dict: Dict[str, Any] = {
        "Description": result.Description,
        "Annotations": {
            "IsAbout": {"TermURL": result.Annotations.IsAbout.TermURL},
            "IsPartOf": (
                {
                    "TermURL": result.Annotations.IsPartOf.get("TermURL", ""),
                    "Label": result.Annotations.IsPartOf.get("Label", ""),
                }
                if result.Annotations.IsPartOf
                else {"TermURL": "", "Label": ""}
            ),
        },
    }

    # Define the expected result as a dictionary
    expected_result_dict: Dict[str, Any] = {
        "Description": "Description of Assessment Tool conducted",
        "Annotations": {
            "IsAbout": {"TermURL": "nb:Assessment"},
            "IsPartOf": {
                "TermURL": "cogatlas:trm_4fbd2af083332",
                "Label": "size match task",
            },
        },
    }

    # Assert that the result matches the expected result
    assert (
        result_dict == expected_result_dict
    ), "The created annotation should match the expected annotation"


# diagnoisFactory tests###########

sample_json_data: str = json.dumps(
    [
        {"label": "Healthy Control", "identifier": "ncit:C94342"},
        {"label": "MDD", "identifier": "snomed:123456789"},
        {"label": "Other", "identifier": "snomed:987654321"},
    ]
)

# Sample parsed output
sample_parsed_output: Dict[str, Any] = {
    "TermURL": "nb:Diagnosis",
    "Levels": {"0": "Healthy Control", "1": "MDD", "2": "Other"},
}


def test_create_annotation_diagnosis() -> None:
    # Mocking the open function to return the sample_json_data
    with patch("builtins.open", mock_open(read_data=sample_json_data)):
        # Create an instance of the DiagnosisFactory
        diagnosis_factory: DiagnosisFactory = DiagnosisFactory(
            mapping_file="fake_path/diagnosisTerms.json"
        )

        # Create the annotation using the sample parsed output
        result: TSVAnnotations = diagnosis_factory.create_annotation(
            sample_parsed_output
        )

        # Expected Levels mapping based on the sample JSON data
        expected_levels: Dict[str, str] = {
            "0": "Healthy Control",
            "1": "MDD",
            "2": "Other",
        }

        # Verify the result
        assert result.Description == "Group variable"
        assert result.Levels == expected_levels
        assert isinstance(result.Annotations, Annotations)
        assert isinstance(result.Annotations.IsAbout, IsAboutGroup)
        assert result.Annotations.IsAbout.Label == "Diagnosis"
        assert result.Annotations.IsAbout.TermURL == "nb:Diagnosis"
