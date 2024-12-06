from typing import Callable
from src.model import Query, QueryGraph, QueryResult


def create_graph(csv_path: str) -> QueryGraph:
    # Read the csv file
    # Create the graph

    def query_graph(query: Query) -> QueryResult:
        result : QueryResult = QueryResult(query=query, matches=[])
        return result

    return query_graph
