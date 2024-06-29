from datetime import datetime
import json
from typing import Dict, Any, Union
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import PromptTemplate
import pytest

from app.categorization.llm_categorization import llm_invocation


@pytest.fixture  # type: ignore
def result_dict1() -> Dict[str, str]:
    return {
        "participant_id": "sub-01 sub-01 sub-02 sub-02 sub-03 sub-03 sub-04 sub-04 sub-05 sub-05",
        "session_id": "ses-01 ses-02 ses-01 ses-02 ses-01 ses-02 ses-01 ses-02 ses-01 ses-02",
        "sex_column": "1,2, 1, 2, missing",
        "pheno_age": "34,1 35,3 nan 39,0 ",
    }


@pytest.fixture  # type: ignore
def result_dict2() -> Dict[str, str]:
    return {
        "session_id": "ses-01 ses-02 ses-01 ses-02 ses-01 ses-02 ses-01 ses-02 ses-01 ses-02",
        "pheno_age": "34,1 35,3 nan 39,0 ",
    }


@pytest.fixture  # type: ignore
def result_dict3() -> Dict[str, str]:
    return {
        "sex_column": "1,2, 1, 2, missing",
        "pheno_age": "34,1 35,3 nan 39,0 ",
    }


@pytest.fixture  # type: ignore
def result_dict4() -> Dict[str, str]:
    return {
        "pheno_age": "34,1 35,3 nan 39,0 ",
    }


def test_Pid(result_dict1: Dict[str, str]) -> None:
    op = json.dumps(llm_invocation(result_dict1), separators=(",", ":"))
    expected_op = """{"TermURL":"nb:ParticipantID"}"""
    assert (
        op == expected_op
    ), f"Participant ID Not successfully categorized. Got {op}"
    print("Participant ID successfully categorized")


def test_Sid(result_dict2: Dict[str, str]) -> None:
    op = json.dumps(llm_invocation(result_dict2), separators=(",", ":"))
    expected_op = """{"TermURL":"nb:Session"}"""
    assert (
        op == expected_op
    ), f"Session ID Not successfully categorized. Got {op}"
    print("Session ID successfully categorized")


def test_Age(result_dict4: Dict[str, str]) -> None:
    op = json.dumps(llm_invocation(result_dict4), separators=(",", ":"))
    expected_op = """{"TermURL":"nb:Age","Format":"europeandecimalvalue"}"""
    assert (
        op.strip() == expected_op.strip()
    ), "Age Not successfully categorized"
    print("Age successfully categorized")


def test_Sex(result_dict3: Dict[str, str]) -> None:
    op = json.dumps(llm_invocation(result_dict3), separators=(",", ":"))
    expected_op = """{"TermURL":"nb:Sex","Levels":{"1":"male","2":"female","3":"other"}}"""
    assert (
        op.strip() == expected_op.strip()
    ), "Sex Not successfully categorized"
    print("Sex successfully categorized")


if __name__ == "__main__":
    pytest.main()
