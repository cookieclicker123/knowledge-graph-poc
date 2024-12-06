import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.networkx_graph import create_graph
from src.model import Query, QueryResult
from src.schema import CSVColumn
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
