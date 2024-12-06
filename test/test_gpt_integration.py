import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import pytest
from src.gpt_service import GPTService

def test_gpt_connection():
    """Test basic connectivity and response from GPT"""
    # Arrange
    gpt_service = GPTService()
    test_prompt = "Say 'test successful' if you can read this"
    
    # Act
    response = gpt_service.get_completion(test_prompt)
    
    # Assert
    assert "test successful" in response.lower()

def test_gpt_service_handles_invalid_input():
    """Test that the service properly validates input"""
    # Arrange
    gpt_service = GPTService()
    invalid_prompt = None
    
    # Act & Assert
    with pytest.raises(ValueError) as exc_info:
        gpt_service.get_completion(invalid_prompt)
    assert "Prompt must be a non-empty string" in str(exc_info.value)

def test_gpt_parse_simple_query():
    """Test that GPT can parse a simple query into our expected format"""
    # Arrange
    gpt_service = GPTService()
    query_text = "Find people who speak English and work at Microsoft"
    
    # Act
    parsed_result = gpt_service.parse_query(query_text)
    
    # Assert
    assert isinstance(parsed_result, list)
    assert len(parsed_result) == 2
    assert ("Person", "SPEAKS", "English") in parsed_result
    assert ("Person", "WORKS_AT", "Microsoft") in parsed_result

def test_gpt_parse_complex_query():
    """Test that GPT can handle more complex queries"""
    # Arrange
    gpt_service = GPTService()
    query_text = "Show me software developers in Canada who speak English and French"
    
    # Act
    parsed_result = gpt_service.parse_query(query_text)
    
    # Assert
    assert isinstance(parsed_result, list)
    assert len(parsed_result) == 4
    assert ("Person", "WORKS_IN", "Software Development") in parsed_result
    assert ("Person", "LIVES_IN", "Canada") in parsed_result
    assert ("Person", "SPEAKS", "English") in parsed_result
    assert ("Person", "SPEAKS", "French") in parsed_result