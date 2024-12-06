import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import pytest
from src.gpt_service import GPTService
from src.networkx_graph import create_graph
from src.model import Query, QueryResult

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

def test_gpt_query_to_graph_results():
    """Test end-to-end flow from natural language to graph results"""
    # Arrange
    gpt_service = GPTService()
    graph_fn = create_graph("test/fixtures/clean_data.csv")
    query_text = "Find people who speak English and work at Microsoft"
    
    # Act
    parsed_conditions = gpt_service.parse_query(query_text)
    query = Query(conditions=parsed_conditions)
    result = graph_fn(query)
    
    # Assert
    assert isinstance(result, QueryResult)
    assert len(result.matches) > 0
    assert any(p.name == "Alaa El-said" for p in result.matches)
    assert all(p.company == "Microsoft" for p in result.matches)
    assert all("English" in p.languages for p in result.matches)

def test_gpt_handles_unsupported_query_types():
    """Test that GPT properly handles queries we don't support"""
    gpt_service = GPTService()
    query_text = "What is the average age of employees?"
    
    with pytest.raises(ValueError) as exc_info:
        gpt_service.parse_query(query_text)
    assert "Unsupported query type" in str(exc_info.value)

def test_gpt_handles_multiple_companies():
    """Test that GPT can handle queries about multiple companies"""
    gpt_service = GPTService()
    query_text = "Find people who work at Microsoft or Amazon"
    parsed = gpt_service.parse_query(query_text)
    
    assert len(parsed) == 2
    assert ("Person", "WORKS_AT", "Microsoft") in parsed
    assert ("Person", "WORKS_AT", "Amazon") in parsed

def test_gpt_normalizes_synonyms():
    """Test that GPT normalizes different ways of saying the same thing"""
    gpt_service = GPTService()
    queries = [
        "Find people who know English",
        "Find English speakers",
        "Find people who can speak English"
    ]
    
    results = [gpt_service.parse_query(q) for q in queries]
    assert all(("Person", "SPEAKS", "English") in r for r in results)
    assert all(len(r) == 1 for r in results)  # Each should only return one condition