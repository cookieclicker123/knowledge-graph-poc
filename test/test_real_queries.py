import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import pytest
from src.gpt_service import GPTService
from src.networkx_graph import create_graph
from src.model import Query

@pytest.fixture
def gpt_service():
    return GPTService()

@pytest.fixture
def graph():
    return create_graph("test/fixtures/clean_data.csv")

def test_find_developers_at_microsoft():
    """Test finding developers at a specific company"""
    gpt_service = GPTService()
    graph = create_graph("test/fixtures/clean_data.csv")
    
    # Parse the natural language query
    conditions = gpt_service.parse_query("Find developers at Microsoft")
    query = Query(conditions=conditions)
    
    # Execute the query
    result = graph(query)
    
    # Verify results
    assert len(result.matches) > 0
    for person in result.matches:
        assert person.company == "Microsoft"
        assert person.industry == "Software Development" 

def test_find_multilingual_developers(gpt_service, graph):
    """Test finding developers who speak multiple languages"""
    conditions = gpt_service.parse_query("Find developers who speak Japanese")
    query = Query(conditions=conditions)
    result = graph(query)
    
    assert len(result.matches) == 2
    for person in result.matches:
        assert person.industry == "Software Development"
        assert "Japanese" in person.languages
        assert person.name in ["Bagus Satya Mas", "Cesar Figueiredo"]

def test_find_by_location(gpt_service, graph):
    """Test finding people by country"""
    conditions = gpt_service.parse_query("Find people in Canada")
    query = Query(conditions=conditions)
    result = graph(query)
    
    assert len(result.matches) == 5
    for person in result.matches:
        assert person.country == "Canada"

def test_find_developers_by_language(gpt_service, graph):
    """Test finding developers by language"""
    conditions = gpt_service.parse_query("Find software developers who speak English")
    query = Query(conditions=conditions)
    result = graph(query)
    
    assert len(result.matches) > 0
    for person in result.matches:
        assert person.industry == "Software Development"
        assert any(lang.lower() in ['english', 'inglês', 'anglais'] 
                  for lang in person.languages)

def test_education_query(gpt_service, graph):
    """Test querying by education"""
    conditions = gpt_service.parse_query(
        "Find people who studied at UCLA"
    )
    query = Query(conditions=conditions)
    result = graph(query)
    
    assert len(result.matches) == 1
    assert result.matches[0].name == "Nick Ramos"
    assert "Los Angeles" in result.matches[0].university

def test_language_normalization(gpt_service, graph):
    """Test querying with different language variations"""
    variations = [
        "Find developers who speak inglês",  # Portuguese
        "Find developers who speak anglais",  # French
        "Find developers who speak English"   # English
    ]
    
    for query in variations:
        conditions = gpt_service.parse_query(query)
        query = Query(conditions=conditions)
        result = graph(query)
        
        # All variations should find English speakers
        assert len(result.matches) > 0
        for person in result.matches:
            assert any(lang.lower() in ['english', 'inglês', 'anglais'] 
                      for lang in person.languages)

def test_university_variations(gpt_service, graph):
    """Test querying with different university name variations"""
    variations = [
        "Find people who studied at UCLA",
        "Find people who studied at University of California, Los Angeles",
        "Find people from UC Los Angeles"
    ]
    
    for query in variations:
        conditions = gpt_service.parse_query(query)
        query = Query(conditions=conditions)
        result = graph(query)
        
        assert len(result.matches) == 1
        assert result.matches[0].name == "Nick Ramos"
        assert "Los Angeles" in result.matches[0].university

def test_complex_multilingual_query(gpt_service, graph):
    """Test complex query with multiple languages and conditions"""
    conditions = gpt_service.parse_query(
        "Find software developers who speak English and Japanese and live in Canada"
    )
    query = Query(conditions=conditions)
    result = graph(query)
    
    assert len(result.matches) == 1
    assert result.matches[0].name == "Cesar Figueiredo"
    assert result.matches[0].industry == "Software Development"
    assert "Japanese" in result.matches[0].languages
    assert any(lang.lower() in ['english', 'inglês', 'anglais'] 
              for lang in result.matches[0].languages)
    assert result.matches[0].country == "Canada" 

def test_mixed_case_queries(gpt_service, graph):
    """Test that queries are case-insensitive"""
    variations = [
        "Find DEVELOPERS who Speak ENGLISH",
        "find developers WHO speak english",
        "FIND DEVELOPERS who speak English"
    ]
    
    for query in variations:
        conditions = gpt_service.parse_query(query)
        query = Query(conditions=conditions)
        result = graph(query)
        assert len(result.matches) > 0
        for person in result.matches:
            assert person.industry == "Software Development"
            assert any(lang.lower() in ['english', 'inglês', 'anglais'] 
                      for lang in person.languages)

def test_multiple_languages_any_order(gpt_service, graph):
    """Test that language order doesn't matter"""
    variations = [
        "Find developers who speak Japanese and English",
        "Find developers who speak English and Japanese",
        "Find people who know English and Japanese"
    ]
    
    for query in variations:
        conditions = gpt_service.parse_query(query)
        query = Query(conditions=conditions)
        result = graph(query)
        assert len(result.matches) > 0
        for person in result.matches:
            assert "Japanese" in person.languages
            assert any(lang.lower() in ['english', 'inglês', 'anglais'] 
                      for lang in person.languages)

def test_partial_company_names(gpt_service, graph):
    """Test matching partial company names"""
    variations = [
        "Find people at Microsoft Corp",
        "Find people at MS",
        "Find people working at Microsoft Corporation"
    ]
    
    for query in variations:
        conditions = gpt_service.parse_query(query)
        query = Query(conditions=conditions)
        result = graph(query)
        assert len(result.matches) > 0
        for person in result.matches:
            assert person.company == "Microsoft"

def test_invalid_queries(gpt_service, graph):
    """Test handling of invalid or malformed queries"""
    invalid_queries = [
        "",  # Empty query
        "   ",  # Whitespace only
        "SELECT * FROM people",  # SQL injection attempt
        123,  # Wrong type
        None  # None value
    ]
    
    for query in invalid_queries:
        with pytest.raises(ValueError):
            conditions = gpt_service.parse_query(query) 