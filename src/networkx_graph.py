import networkx as nx
import pandas as pd
from typing import Callable
from src.model import Query, QueryGraph, QueryResult


def create_graph(csv_path: str) -> QueryGraph:
    # Read the CSV file
    df = pd.read_csv(csv_path)
    
    # Create a directed graph
    G = nx.DiGraph()
    
    # Add nodes and edges for each person
    for _, row in df.iterrows():
        person_name = row['name']
        
        # Add WORKS_AT relationship
        if pd.notna(row['company']):
            G.add_edge(person_name, row['company'], relation='WORKS_AT')
        
        # Add SPEAKS relationships
        if pd.notna(row['languages']):
            languages = row['languages'].split('|')
            for lang in languages:
                G.add_edge(person_name, lang, relation='SPEAKS')

    def query_graph(query: Query) -> QueryResult:
        matches = []
        # For each person in the graph
        for node in G.nodes():
            matches_all = True
            # Check if they satisfy all conditions
            for subject, relation, object in query.conditions:
                edges = list(G.out_edges(node, data=True))
                if not any(edge[1] == object and edge[2]['relation'] == relation for edge in edges):
                    matches_all = False
                    break
            if matches_all:
                matches.append(node)
                
        return QueryResult(query=query, matches=matches)

    return query_graph
