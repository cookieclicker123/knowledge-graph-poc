# Knowledge Graph POC
This repo is for trying out solutions to search a knowledge graph for nodes that match a query.

## Installation

```bash
 git clone git@github.com:cookieclicker123/knowledge-graph-poc.git
 cd knowledge-graph-poc
```

### Virtual environment

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Run the tests

```bash
pytest test/test_graph.py
pytest test/test_gpt_integration.py
pytest test/test_edge_cases.py
```

## Requirements

### Graph

Using the csv test data in clean_data.csv create a knowledge graph with the following types of Nodes:

- Person
- University
- Company
- Language (Note that languages need to be split out from the languages column)
- Industry
- Country

With the following Edges

Person -> University
Person -> Langauge
Person -> Industry
Person -> Country
Person -> Company

### Queries

1. Find all People who work at Microsoft and speak English
