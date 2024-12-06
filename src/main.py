import sys
from pathlib import Path
from typing import Optional
import textwrap



from src.config import (
    DEFAULT_DATA_PATH, 
    PROMPT_SYMBOL, 
    EXIT_COMMANDS, 
    HELP_COMMANDS,
    HELP_TEXT
)
from src.gpt_service import GPTService
from src.networkx_graph import create_graph
from src.model import Query

class ChatInterface:
    def __init__(self, data_path: Optional[Path] = None):
        """Initialize the chat interface with data path"""
        try:
            self.data_path = data_path or DEFAULT_DATA_PATH
            self.gpt_service = GPTService(str(self.data_path))
            self.graph = create_graph(str(self.data_path))
            print(f"✨ Initialized with data from: {self.data_path}")
        except Exception as e:
            print(f"❌ Error initializing: {str(e)}")
            sys.exit(1)

    def format_person(self, person) -> str:
        """Format a person's details for display"""
        return textwrap.dedent(f"""
            👤 {person.name}
            🏢 Company: {person.company}
            🎓 University: {person.university}
            🌍 Country: {person.country}
            💼 Industry: {person.industry}
            🗣️ Languages: {', '.join(person.languages)}
        """).strip()

    def handle_query(self, query_text: str) -> None:
        """Process a single query and display results"""
        try:
            # Parse query using GPT
            conditions = self.gpt_service.parse_query(query_text)
            query = Query(conditions=conditions)
            
            # Execute query on graph
            results = self.graph(query)
            
            # Display results
            if not results.matches:
                print("\n😕 No matches found.")
                return
                
            print(f"\n✨ Found {len(results.matches)} match(es):")
            for person in results.matches:
                print("\n" + self.format_person(person))
                
        except ValueError as e:
            print(f"\n❌ Error: {str(e)}")
        except Exception as e:
            print(f"\n❌ Unexpected error: {str(e)}")

    def run(self) -> None:
        """Run the main chat loop"""
        print("\n👋 Welcome to the Knowledge Graph Query Interface!")
        print("Type 'help' for usage information or 'quit' to exit.")
        
        while True:
            try:
                # Get user input
                query = input(f"\n{PROMPT_SYMBOL}").strip()
                
                # Handle special commands
                if not query:
                    continue
                if query.lower() in EXIT_COMMANDS:
                    print("\n👋 Goodbye!")
                    break
                if query.lower() in HELP_COMMANDS:
                    print(HELP_TEXT)
                    continue
                    
                # Process regular query
                self.handle_query(query)
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Unexpected error: {str(e)}")

def main():
    """Entry point for the application"""
    # Parse command line arguments if needed
    data_path = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    
    # Run the chat interface
    chat = ChatInterface(data_path)
    chat.run()

if __name__ == "__main__":
    main() 