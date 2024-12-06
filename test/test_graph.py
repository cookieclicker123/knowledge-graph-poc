import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.networkx_graph import create_graph
from src.model import Query, QueryResult
from src.schema import CSVColumn
from src.query_parser import parse_query_intent
import pytest

def test_create_graph():
    # Arrange & Act
    graph_fn = create_graph("test/fixtures/clean_data.csv")
    
    # Assert
    assert callable(graph_fn)

def test_create_graph_validates_columns():
    # Arrange
    csv_content = "random_column,other_column\n1,2"
    with open("test/fixtures/invalid_columns.csv", "w") as f:
        f.write(csv_content)
    
    # Act & Assert
    with pytest.raises(ValueError) as exc_info:
        create_graph("test/fixtures/invalid_columns.csv")
    
    # Assert both the error and the expected columns from enum
    error_message = str(exc_info.value)
    assert "Invalid CSV columns" in error_message
    assert f"Expected: {[col.value for col in CSVColumn]}" in error_message

def test_find_microsoft_english_speakers():
    # Arrange
    graph_fn = create_graph("test/fixtures/clean_data.csv")
    query = Query(
        conditions=[
            ("Person", "WORKS_AT", "Microsoft"),
            ("Person", "SPEAKS", "English")
        ]
    )
    
    # Act
    result = graph_fn(query)
    
    # Assert
    assert isinstance(result, QueryResult)
    assert len(result.matches) > 0
    assert any(person for person in result.matches)

def test_empty_result_for_invalid_query():
    # Arrange
    graph_fn = create_graph("test/fixtures/clean_data.csv")
    query = Query(
        conditions=[
            ("Person", "WORKS_AT", "NonExistentCompany"),
            ("Person", "SPEAKS", "English")
        ]
    )
    
    # Act
    result = graph_fn(query)
    
    # Assert
    assert isinstance(result, QueryResult)
    assert len(result.matches) == 0

def test_query_returns_complete_person_profiles():
    # Arrange
    graph_fn = create_graph("test/fixtures/clean_data.csv")
    query = Query(
        conditions=[
            ("Person", "WORKS_AT", "Microsoft"),
            ("Person", "SPEAKS", "English")
        ]
    )
    
    # Act
    result = graph_fn(query)
    
    # Assert
    assert len(result.matches) > 0
    person = result.matches[0]
    
    # We know Alaa El-said should be in the results
    assert person.id == "alaa-el-said-56740659"
    assert person.name == "Alaa El-said"
    assert person.company == "Microsoft"
    assert person.university == "Mansoura University"
    assert "Arabic" in person.languages
    assert "English" in person.languages
    assert person.industry == "Software Development"
    assert person.country == "Saudi Arabia"

def test_all_relationships_are_created():
    # Arrange
    graph_fn = create_graph("test/fixtures/clean_data.csv")
    
    # Test each relationship individually
    university_query = Query(conditions=[("Person", "STUDIED_AT", "Mansoura University")])
    language_query = Query(conditions=[("Person", "SPEAKS", "Arabic")])
    industry_query = Query(conditions=[("Person", "WORKS_IN", "Software Development")])
    country_query = Query(conditions=[("Person", "LIVES_IN", "Saudi Arabia")])
    company_query = Query(conditions=[("Person", "WORKS_AT", "Microsoft")])
    
    # Act & Assert
    # We know Alaa El-said should match all these
    for query in [university_query, language_query, industry_query, country_query, company_query]:
        result = graph_fn(query)
        assert len(result.matches) > 0
        assert any(p.name == "Alaa El-said" for p in result.matches)

def test_complex_query_with_three_conditions():
    # Arrange
    graph_fn = create_graph("test/fixtures/clean_data.csv")
    query = Query(
        conditions=[
            ("Person", "SPEAKS", "English"),
            ("Person", "WORKS_IN", "Software Development"),
            ("Person", "LIVES_IN", "United States")
        ]
    )
    
    # Act
    result = graph_fn(query)
    
    # Assert
    assert len(result.matches) > 0
    # Verify specific person that matches all conditions
    assert any(p.name == "Lauren Calderon" for p in result.matches)

def test_parse_natural_language_query():
    # Arrange
    query_text = "Find people who speak English and work at Microsoft"
    expected_conditions = [
        ("Person", "SPEAKS", "English"),
        ("Person", "WORKS_AT", "Microsoft")
    ]
    
    # Act
    parsed_query = parse_query_intent(query_text)
    
    # Assert
    assert isinstance(parsed_query, Query)
    assert parsed_query.conditions == expected_conditions
