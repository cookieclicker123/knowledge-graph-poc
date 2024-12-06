import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import pytest
from src.gpt_service import GPTService
from src.networkx_graph import create_graph
from src.model import Query, QueryResult

def test_ambiguous_industry():
    """Test handling of ambiguous industry terms"""
    gpt_service = GPTService()
    queries = [
        "Find developers",  # Ambiguous - could be many types
        "Find people in development",
        "Show me people working in dev"
    ]
    
    for query in queries:
        parsed = gpt_service.parse_query(query)
        assert ("Person", "WORKS_IN", "Software Development") in parsed

def test_partial_company_names():
    """Test handling of partial/informal company names"""
    gpt_service = GPTService()
    queries = [
        "Find people at MS",  # Should match Microsoft
        "Find people working at Capgemini India"  # Should match Capgemini
    ]
    
    parsed1 = gpt_service.parse_query(queries[0])
    assert ("Person", "WORKS_AT", "Microsoft") in parsed1
    
    parsed2 = gpt_service.parse_query(queries[1])
    assert ("Person", "WORKS_AT", "Capgemini") in parsed2

def test_mixed_language_queries():
    """Test queries mixing languages and other conditions"""
    gpt_service = GPTService()
    query = "Find developers who speak English and Japanese in Canada"
    
    parsed = gpt_service.parse_query(query)
    assert ("Person", "SPEAKS", "Inglês") in parsed
    assert ("Person", "SPEAKS", "Japanese") in parsed
    assert ("Person", "WORKS_IN", "Software Development") in parsed
    assert ("Person", "LIVES_IN", "Canada") in parsed

def test_empty_result_handling():
    """Test handling queries that would yield no results"""
    gpt_service = GPTService()
    graph_fn = create_graph("test/fixtures/clean_data.csv")
    query_text = "Find people who speak Klingon"  # Definitely not in our dataset
    
    parsed_conditions = gpt_service.parse_query(query_text)
    query = Query(conditions=parsed_conditions)
    result = graph_fn(query)
    
    assert isinstance(result, QueryResult)
    assert len(result.matches) == 0  # Should return empty list, not error

def test_case_insensitive_matching():
    """Test that queries are case insensitive"""
    gpt_service = GPTService()
    queries = [
        "find ENGLISH speakers at MICROSOFT",
        "Find english Speakers at microsoft",
        "FIND English speakers AT Microsoft"
    ]
    
    results = [gpt_service.parse_query(q) for q in queries]
    expected = [
        ("Person", "SPEAKS", "Inglês"),
        ("Person", "WORKS_AT", "Microsoft")
    ]
    
    assert all(all(condition in result for condition in expected) for result in results)

def debug_gpt_response():
    """Debug helper to see raw GPT responses"""
    gpt_service = GPTService()
    
    # Test case 1: Ambiguous industry
    print("\n=== Ambiguous Industry Test ===")
    response = gpt_service.client.chat.completions.create(
        model=gpt_service.model,
        messages=[
            {"role": "system", "content": gpt_service.parse_query.__doc__},
            {"role": "user", "content": "Find developers"}
        ],
        temperature=0.1
    )
    print(response.choices[0].message.content)
    
    # Test case 2: Partial company name
    print("\n=== Partial Company Name Test ===")
    response = gpt_service.client.chat.completions.create(
        model=gpt_service.model,
        messages=[
            {"role": "system", "content": gpt_service.parse_query.__doc__},
            {"role": "user", "content": "Find people at MS"}
        ],
        temperature=0.1
    )
    print(response.choices[0].message.content)
    
    # Test case 3: Mixed language query
    print("\n=== Mixed Language Query Test ===")
    response = gpt_service.client.chat.completions.create(
        model=gpt_service.model,
        messages=[
            {"role": "system", "content": gpt_service.parse_query.__doc__},
            {"role": "user", "content": "Find developers who speak English and Japanese in Canada"}
        ],
        temperature=0.1
    )
    print(response.choices[0].message.content) 