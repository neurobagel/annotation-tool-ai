import pytest
from unittest.mock import patch, MagicMock
from app.categorization.llm_categorization import SexLevel, AgeFormat, llm_invocation

@pytest.fixture
def mock_llm_response():
    with patch('app.categorization.llm_categorization.ChatOllama') as MockChatOllama:
        instance = MockChatOllama.return_value
        instance.invoke = MagicMock()
        yield instance.invoke

def test_sex_level():
    result_dict = {"key1": "male"}
    output = SexLevel(result_dict, "", "key1")
    expected_output = {
        "TermURL": "nb:Sex",
        "Levels": {"m": "male", "f": "female", "o": "other"}
    }
    assert output == expected_output

def test_age_format():
    result_dict = {"key1": "34 35.3 NA"}
    output = AgeFormat(result_dict, "", "key1")
    expected_output = {
        "TermURL": "nb:Age",
        "Format": "integervalue"
    }
    assert output == expected_output

def test_llm_invocation(mock_llm_response):
    # Test case 1
    result_dict = {"pheno_sex": "1 2 1 2 missing missing"}
    mock_llm_response.return_value = "Sex"
    with patch('app.categorization.llm_categorization.PromptTemplate') as MockPromptTemplate:
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = "Sex"
        MockPromptTemplate.return_value.__or__.return_value = mock_chain
        output = llm_invocation(result_dict)
        expected_output = {
            "TermURL": "nb:Sex",
            "Levels": {"1": "male", "2": "female", "3": "other"}
        }
        assert output == expected_output

    # Test case 2
    result_dict = {"participant_id": "sub-01 sub-02 sub-03"}
    mock_llm_response.return_value = "Participant_IDs"
    with patch('app.categorization.llm_categorization.PromptTemplate') as MockPromptTemplate:
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = "Participant_IDs"
        MockPromptTemplate.return_value.__or__.return_value = mock_chain
        output = llm_invocation(result_dict)
        expected_output = {"TermURL": "nb:ParticipantID"}
        assert output == expected_output

    # Test case 3
    result_dict = {"session_id": "ses-01 ses-02"}
    mock_llm_response.return_value = "Session_IDs"
    with patch('app.categorization.llm_categorization.PromptTemplate') as MockPromptTemplate:
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = "Session_IDs"
        MockPromptTemplate.return_value.__or__.return_value = mock_chain
        output = llm_invocation(result_dict)
        expected_output = {"TermURL": "nb:Session"}
        assert output == expected_output

    # Test case 4
    result_dict = {"pheno_age": "34.1 35.3 NA"}
    mock_llm_response.return_value = "Age"
    with patch('app.categorization.llm_categorization.PromptTemplate') as MockPromptTemplate:
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = "Age"
        MockPromptTemplate.return_value.__or__.return_value = mock_chain
        output = llm_invocation(result_dict)
        expected_output = {
            "TermURL": "nb:Age",
            "Format": "floatvalue"
        }
        assert output == expected_output
