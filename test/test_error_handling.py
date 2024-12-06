import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import pytest
from unittest.mock import patch
from openai import OpenAIError
from src.gpt_service import GPTService

def test_invalid_api_key():
    """Test handling of invalid API key"""
    with patch.dict('os.environ', {'OPENAI_API_KEY': 'invalid_key'}):
        with pytest.raises(ValueError) as exc_info:
            GPTService().parse_query("Find developers")
        assert "Incorrect API key provided" in str(exc_info.value)

def test_network_failure():
    """Test handling of OpenAI API network failures"""
    gpt_service = GPTService()
    
    with patch.object(gpt_service.client.chat.completions, 'create') as mock_create:
        mock_create.side_effect = OpenAIError("Network error")
        
        with pytest.raises(ValueError) as exc_info:
            gpt_service.parse_query("Find developers")
        assert "Failed to parse query" in str(exc_info.value)

def test_malformed_data():
    """Test handling of malformed CSV data"""
    with pytest.raises(ValueError) as exc_info:
        GPTService(data_path="test/fixtures/malformed_data.csv")
    assert "Failed to load company data" in str(exc_info.value)

def test_invalid_query_format():
    """Test handling of invalid query formats"""
    gpt_service = GPTService()
    invalid_queries = [
        "",  # Empty query
        "   ",  # Whitespace only
        None,  # None
        123,  # Wrong type
        "SELECT * FROM people"  # SQL injection attempt
    ]
    
    for query in invalid_queries:
        with pytest.raises(ValueError) as exc_info:
            gpt_service.parse_query(query)
        assert "Invalid query format" in str(exc_info.value)

def test_timeout_handling():
    """Test handling of API timeout"""
    gpt_service = GPTService()
    
    with patch.object(gpt_service.client.chat.completions, 'create') as mock_create:
        mock_create.side_effect = TimeoutError("Request timed out")
        
        with pytest.raises(ValueError) as exc_info:
            gpt_service.parse_query("Find developers")
        assert "Request timed out" in str(exc_info.value) 