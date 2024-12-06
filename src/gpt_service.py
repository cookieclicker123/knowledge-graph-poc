import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

class GPTService:
    def __init__(self):
        self.client = OpenAI()  # Will automatically use OPENAI_API_KEY from env
        self.model = "gpt-4-turbo-preview"

    def get_completion(self, prompt: str) -> str:
        """Get a completion from GPT-4 Turbo"""
        if not prompt or not isinstance(prompt, str):
            raise ValueError("Prompt must be a non-empty string")
            
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that helps parse queries about people, their work, languages, and locations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            return response.choices[0].message.content
        except Exception as e:
            raise ConnectionError(f"Failed to get GPT completion: {str(e)}")

    def parse_query(self, query_text: str) -> list[tuple[str, str, str]]:
        """Parse a natural language query into graph query conditions"""
        system_prompt = """
        You are a query parser that converts natural language queries about people into structured conditions.
        Output should be a list of tuples in the format: [("Person", "RELATION", "Object")]
        
        Valid relations are:
        - SPEAKS (for languages) - Use for: speaks, knows, can speak, is fluent in
        - WORKS_AT (for companies) - Use for: employed at, works for, is at
        - WORKS_IN (for industries) - Use for: works in, specializes in, focused on
        - LIVES_IN (for countries) - Use for: based in, located in, resides in
        - STUDIED_AT (for universities) - Use for: graduated from, attended, studied at
        
        For unsupported operations (like counting, averaging, statistics), return exactly: "ERROR: Unsupported query type"
        
        Examples:
        "Find people who speak English and work at Microsoft"
        → [("Person", "SPEAKS", "English"), ("Person", "WORKS_AT", "Microsoft")]
        
        "What's the average age of employees?"
        → "ERROR: Unsupported query type"
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query_text}
                ],
                temperature=0.1
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Check for error message first
            if result_text.startswith("ERROR:"):
                raise ValueError(result_text)
            
            # Clean and evaluate the string to get the list of tuples
            result_text = result_text.strip('`')
            if 'python' in result_text.lower():
                result_text = result_text.split('\n', 1)[1]
            
            try:
                conditions = eval(result_text)
                if not all(
                    isinstance(item, tuple) and 
                    len(item) == 3 and 
                    all(isinstance(x, str) for x in item)
                    for item in conditions
                ):
                    raise ValueError("Invalid format in GPT response")
                
                # Case standardization rules
                standardization_rules = {
                    "WORKS_IN": str.title,      # Software Development
                    "WORKS_AT": str.title,      # Microsoft
                    "SPEAKS": str.title,        # English
                    "LIVES_IN": str.title,      # United States
                    "STUDIED_AT": str.title,    # University Name
                }
                
                # Apply standardization
                standardized_conditions = []
                for subject, relation, obj in conditions:
                    if relation in standardization_rules:
                        obj = standardization_rules[relation](obj)
                    standardized_conditions.append((subject, relation, obj))
                
                return standardized_conditions
                
            except Exception as e:
                raise ValueError(f"Failed to parse GPT response into tuples: {str(e)}")
                
        except Exception as e:
            raise ValueError(f"Failed to parse query: {str(e)}") 