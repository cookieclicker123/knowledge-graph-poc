from src.model import Query, QueryResult


def create_graph(csv_path: str):
    # Read the csv file
    # Create the graph
    
    def query_graph(query: Query) -> QueryResult:
        result : QueryResult = QueryResult(query=query, matches=[])
        return result
    
    return query_graph