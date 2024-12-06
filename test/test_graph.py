import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.networkx_graph import create_graph
from src.model import Query, QueryResult
import pytest

def test_create_graph():
    # Arrange
    graph_fn = create_graph("test/fixtures/clean_data.csv")
    
    # Assert
    assert callable(graph_fn)

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
