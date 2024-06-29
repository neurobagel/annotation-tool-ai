from datetime import datetime
import json
from typing import Dict, Any, Union
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import PromptTemplate

from app.categorization.llm_categorization import llm_invocation


def test_Pid(result_dict: Dict[str, str]) -> None:
    op = json.dumps(llm_invocation(result_dict), separators=(",", ":"))
    expected_op = """{"TermURL":"nb:ParticipantID"}"""
    assert (
        op == expected_op
    ), f"Participant ID Not successfully categorized. Got {op}"
    print("Participant ID successfully categorized")


def test_Sid(result_dict: Dict[str, str]) -> None:
    op = json.dumps(llm_invocation(result_dict), separators=(",", ":"))
    expected_op = """{"TermURL":"nb:Session"}"""
    print(f"Actual Output: {op}")
    print(f"Expected Output: {expected_op.strip()}")
    assert (
        op == expected_op
    ), f"Session ID Not successfully categorized. Got {op}"
    print("Session ID successfully categorized")


def test_Age(result_dict: Dict[str, str]) -> None:
    op = json.dumps(llm_invocation(result_dict), separators=(",", ":"))
    expected_op = """ {"TermURL":"nb:Age","Format":"europeandecimalvalue"} """
    print(f"Actual Output: {op}")
    print(f"Expected Output: {expected_op.strip()}")
    assert (
        op.strip() == expected_op.strip()
    ), " Age Not successfully categorized"
    print("Agesuccessfully categorized")


def test_Sex(result_dict: Dict[str, str]) -> None:
    op = json.dumps(llm_invocation(result_dict), separators=(",", ":"))
    expected_op = """{"TermURL":"nb:Sex","Levels":{"1":"male","2":"female","3":"other"}}"""

    # Debugging prints
    print(f"Actual Output: {op}")
    print(f"Expected Output: {expected_op.strip()}")

    assert (
        op.strip() == expected_op.strip()
    ), "Sex Not successfully categorized"
    print("Sex successfully categorized")  # Invoke LLM


if __name__ == "__main__":
    result_dict1 = {
        "participant_id": "sub-01 sub-01 sub-02 sub-02 \
            sub-03 sub-03 sub-04 sub-04 sub-05 sub-05",
        "session_id": "ses-01 ses-02 ses-01 ses-02 ses-01 \
              ses-02 ses-01 ses-02 ses-01 ses-02",
        "sex_column": "1,2, 1, 2, missing",
        "pheno_age": "34,1 35,3 nan 39,0 ",
    }
    result_dict2 = {
        # "participant_id": "sub-01 sub-01 sub-02 sub-02 \
        #     sub-03 sub-03 sub-04 sub-04 sub-05 sub-05",
        "session_id": "ses-01 ses-02 ses-01 ses-02 ses-01 \
              ses-02 ses-01 ses-02 ses-01 ses-02",
        # "sex_column": "1,2, 1, 2, missing",
        "pheno_age": "34,1 35,3 nan 39,0 ",
    }
    result_dict3 = {
        # "participant_id": "sub-01 sub-01 sub-02 sub-02 \
        #     sub-03 sub-03 sub-04 sub-04 sub-05 sub-05",
        # "session_id": "ses-01 ses-02 ses-01 ses-02 ses-01 \
        #       ses-02 ses-01 ses-02 ses-01 ses-02",
        "sex_column": "1,2, 1, 2, missing",
        "pheno_age": "34,1 35,3 nan 39,0 ",
    }
    result_dict4 = {
        # "participant_id": "sub-01 sub-01 sub-02 sub-02 \
        #     sub-03 sub-03 sub-04 sub-04 sub-05 sub-05",
        # "session_id": "ses-01 ses-02 ses-01 ses-02 ses-01 \
        #       ses-02 ses-01 ses-02 ses-01 ses-02",
        # "sex_column": "1,2, 1, 2, missing",
        "pheno_age": "34,1 35,3 nan 39,0 ",
    }
    test_Pid(result_dict1)
    test_Sid(result_dict2)
    test_Sex(result_dict3)
    test_Age(result_dict4)
