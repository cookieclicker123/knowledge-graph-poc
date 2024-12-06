from pathlib import Path

# Data paths
DEFAULT_DATA_PATH = Path("test/fixtures/clean_data.csv")

# Chat interface settings
PROMPT_SYMBOL = "🔍 "
EXIT_COMMANDS = {"quit", "exit", "bye", "q"}
HELP_COMMANDS = {"help", "?", "h"}

# Help text
HELP_TEXT = """
Available Commands:
------------------
help, ?, h     - Show this help message
quit, exit, q  - Exit the application

Query Examples:
--------------
- Find developers who speak English
- Find people who work at Microsoft
- Show me software developers in Canada
- Find people who speak English and Japanese
- Find developers at Amazon who speak multiple languages

Tips:
-----
- Queries are case-insensitive
- You can search by: language, company, location, industry, university
- Use natural language - no special syntax needed
""" 