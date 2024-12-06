import networkx as nx
import pandas as pd
from src.model import Query, QueryGraph, QueryResult
from src.schema import CSVColumn


def create_graph(csv_path: str) -> QueryGraph:
    # Read the CSV file
    df = pd.read_csv(csv_path)
    
    # Validate columns using enum
    required_columns = {col.value for col in CSVColumn}
    if set(df.columns) != required_columns:
        raise ValueError(f"Invalid CSV columns. Expected: {[col.value for col in CSVColumn]}")
    
    # Create a directed graph
    G = nx.DiGraph()
    
    # Add nodes and edges for each person
    for _, row in df.iterrows():
        person_name = row[CSVColumn.NAME.value]
        
        # Add WORKS_AT relationship
        if pd.notna(row[CSVColumn.COMPANY.value]):
            G.add_edge(person_name, row[CSVColumn.COMPANY.value], relation='WORKS_AT')
        
        # Add SPEAKS relationships
        if pd.notna(row[CSVColumn.LANGUAGES.value]):
            languages = row[CSVColumn.LANGUAGES.value].split('|')
            for lang in languages:
                G.add_edge(person_name, lang, relation='SPEAKS')

    def query_graph(query: Query) -> QueryResult:
        matches = []
        for node in G.nodes():
            matches_all = True
            for subject, relation, object in query.conditions:
                edges = list(G.out_edges(node, data=True))
                if not any(edge[1] == object and edge[2]['relation'] == relation for edge in edges):
                    matches_all = False
                    break
            if matches_all:
                matches.append(node)
                
        return QueryResult(query=query, matches=matches)

    return query_graph
