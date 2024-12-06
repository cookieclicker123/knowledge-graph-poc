# Knowledge Graph POC
This repo is for trying out solutions to search a knowledge graph for nodes that match a query.

## Installation

```bash
git clone git@github.com:cookieclicker123/knowledge-graph-poc.git
cd knowledge-graph-poc
```

### Virtual Environment Setup

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Development Installation

```bash
# Install package in editable mode
pip install -e .
```

### Environment Variables

```bash
# Create .env file with your OpenAI API key
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

## Running the Application

You can run the chat interface in two ways:

```bash
# Method 1 - Using the entry point
kgraph

# Method 2 - Using Python directly
python -m src.main
```

### Example Queries
- "Find people who speak English"
- "Find developers at Microsoft"
- "Show me software developers in Canada who speak Japanese"
- "Find people who work in healthcare and speak Spanish"

## Running the Tests

```bash
# Run individual test suites
pytest test/test_graph.py
pytest test/test_gpt_integration.py
pytest test/test_edge_cases.py
pytest test/test_error_handling.py
pytest test/test_real_queries.py

# Or run all tests
pytest test/
```

## Technical Details

### Graph Structure

Using the CSV test data in clean_data.csv creates a knowledge graph with the following types of Nodes:

- Person
- University
- Company
- Language (Note that languages need to be split out from the languages column)
- Industry
- Country

With the following Edges:

- Person -> University (STUDIED_AT)
- Person -> Language (SPEAKS)
- Person -> Industry (WORKS_IN)
- Person -> Country (LIVES_IN)
- Person -> Company (WORKS_AT)

### Features
- Natural language query processing using GPT-4
- Flexible language matching (handles variations like English/Inglês)
- Company name normalization
- Comprehensive error handling
- Interactive chat interface



