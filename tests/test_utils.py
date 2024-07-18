import pytest
from typing import Dict
from app.utils.process_llm_output import process_llm_output
from app.products.tsv_annotations import TSVAnnotations
from app.utils.value_validation import (
    is_integer,
    is_float,
    is_iso8601,
    is_european_decimal,
    is_bounded,
    is_years,
)
from app.utils.data_transformers import SexLevel, AgeFormat
from unittest.mock import patch, MagicMock
from app.utils.llm_invocation import llm_invocation

# data_transformers test ##########


def test_sex_level() -> None:
    result_dict: Dict[str, str] = {"m": "male"}
    output = SexLevel(result_dict, "", "m")
    expected_output = {
        "TermURL": "nb:Sex",
        "Levels": {"m": "male", "f": "female", "o": "other"},
    }
    assert output == expected_output


def test_age_format() -> None:
    result_dict: Dict[str, str] = {"age": "34 35.3 NA"}
    output = AgeFormat(result_dict, "", "age")
    expected_output = {"TermURL": "nb:Age", "Format": "integervalue"}
    assert output == expected_output


# llm_invocation test ##############


@pytest.fixture  # type: ignore
def mock_factory_context_create() -> MagicMock:  # type: ignore
    with patch(
        "app.factories.llm_factories.factory_context.FactoryContext.create"
    ) as mock:
        yield mock


@pytest.fixture  # type: ignore
def mock_factory_llm_get_factories() -> MagicMock:  # type: ignore
    with patch(
        "app.factories.llm_factories.llm_factory_manager.FactoryLLM.get_factories"  # noqa: E501
    ) as mock:
        mock.return_value = MagicMock()
        yield mock


def test_llm_invocation(
    mock_factory_context_create: MagicMock,
    mock_factory_llm_get_factories: MagicMock,
) -> None:
    # Setup
    result_dict: Dict[str, str] = {"pheno_sex": "1 2 1 2 missing missing"}
    expected_output: Dict[str, str] = {"TermURL": "nb:Sex"}
    mock_factory_context_create.return_value = expected_output

    # Exercise
    actual_output = llm_invocation(result_dict)

    # Verify
    mock_factory_context_create.assert_called_once_with(
        "pheno_sex", "1 2 1 2 missing missing"
    )
    assert (
        actual_output == expected_output
    ), "The llm_invocation function did not return the expected output."


# process_llm_output test ###########


def test_process_llm_output_success() -> None:
    # Assuming this is the input to process_llm_output
    parsed_output: Dict[str, str] = {"TermURL": "nb:ParticipantID"}

    expected_result: TSVAnnotations = TSVAnnotations(
        Description="A participant ID",
        Annotations={
            "IsAbout": {
                "Label": "Subject Unique Identifier",
                "TermURL": "nb:ParticipantID",
            },
            "Identifies": "participant",
        },
    )

    # Step 3: Call the function with real dependencies
    result = process_llm_output(parsed_output)  # type: ignore

    # Step 4: Assert expected behavior
    assert isinstance(result, TSVAnnotations)
    assert result.Description == expected_result.Description
    assert (
        result.Annotations.IsAbout.Label
        == expected_result.Annotations["IsAbout"]["Label"]
    )
    assert (
        result.Annotations.IsAbout.TermURL
        == expected_result.Annotations["IsAbout"]["TermURL"]
    )
    assert (
        result.Annotations.Identifies
        == expected_result.Annotations["Identifies"]
    )


# validate_input test ###############


@pytest.mark.parametrize(
    "input_string, expected_result",
    [
        ("123", True),
        ("456.78", False),
        ("abc", False),
    ],
)  # type: ignore
def test_is_integer(input_string: str, expected_result: bool) -> None:
    assert is_integer(input_string) == expected_result


@pytest.mark.parametrize(
    "input_string, expected_result",
    [
        ("123", True),
        ("456.78", True),
        ("abc", False),
    ],
)  # type: ignore
def test_is_float(input_string: str, expected_result: bool) -> None:
    assert is_float(input_string) == expected_result


@pytest.mark.parametrize(
    "input_string, expected_result",
    [
        ("2023-07-18", True),
        ("2023-07-18T12:00:00", True),
        ("abc", False),
    ],
)  # type: ignore
def test_is_iso8601(input_string: str, expected_result: bool) -> None:
    assert is_iso8601(input_string) == expected_result


@pytest.mark.parametrize(
    "input_string, expected_result",
    [
        ("123.45", False),
        ("123,45", True),
        ("abc", False),
    ],
)  # type: ignore
def test_is_european_decimal(input_string: str, expected_result: bool) -> None:
    assert is_european_decimal(input_string) == expected_result


@pytest.mark.parametrize(
    "input_string, expected_result",
    [
        ("10+", True),
        ("20", False),
        ("abc", False),
    ],
)  # type: ignore
def test_is_bounded(input_string: str, expected_result: bool) -> None:
    assert is_bounded(input_string) == expected_result


@pytest.mark.parametrize(
    "input_string, expected_result",
    [
        ("10y", True),
        ("abc", False),
    ],
)  # type: ignore
def test_is_years(input_string: str, expected_result: bool) -> None:
    assert is_years(input_string) == expected_result
