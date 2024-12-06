import os
from dotenv import load_dotenv
from openai import OpenAI
from typing import Dict, Set, Optional, Any
import re
import pandas as pd

load_dotenv()

class GPTService:
    def __init__(self, data_path: str = "test/fixtures/clean_data.csv"):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        try:
            self.client = OpenAI()
            self.model = "gpt-4-turbo-preview"
            self.company_mappings = self._build_company_mappings(data_path)
        except Exception as e:
            raise ValueError(f"Failed to initialize GPT service: {str(e)}")

    def _build_company_mappings(self, data_path: str) -> Dict[str, str]:
        """Build mappings of company name variations from the CSV data"""
        try:
            df = pd.read_csv(data_path)
            required_columns = {'id', 'name', 'company', 'university', 'languages', 'industry', 'country'}
            if not required_columns.issubset(df.columns):
                raise ValueError("CSV file missing required columns")
            
            companies = set(df['company'].dropna().unique())
            mappings = {}
            
            for company in companies:
                # Full name
                mappings[company.lower()] = company
                
                # Without suffixes
                base_name = re.sub(r'\s+(?:Inc|Ltd|LLC|Limited|Corp|Corporation|India|UK|US)\.?\s*$', '', company)
                if base_name != company:
                    mappings[base_name.lower()] = company
                
                # Abbreviations for multi-word companies
                words = base_name.split()
                if len(words) > 1:
                    abbrev = ''.join(word[0] for word in words)
                    mappings[abbrev.lower()] = company
                    mappings[words[0].lower()] = company
            
            return mappings
            
        except Exception as e:
            raise ValueError(f"Failed to load company data: {str(e)}")

    def normalize_company_name(self, company: str) -> str:
        """Find the best matching company name from our known companies"""
        company_lower = company.lower()
        
        # Direct match
        if company_lower in self.company_mappings:
            return self.company_mappings[company_lower]
        
        # Partial match
        for known_name, canonical_name in self.company_mappings.items():
            if known_name in company_lower or company_lower in known_name:
                return canonical_name
        
        return company

    def parse_query(self, query_text: Any) -> list[tuple[str, str, str]]:
        """Parse a natural language query into graph query conditions"""
        # Type check
        if not isinstance(query_text, str):
            raise ValueError("Invalid query format: Query must be a string")
        
        # Empty or whitespace
        if not query_text or not query_text.strip():
            raise ValueError("Invalid query format: Query cannot be empty")
        
        # SQL injection attempt
        if any(keyword in query_text.upper() for keyword in ["SELECT", "INSERT", "UPDATE", "DELETE", "DROP"]):
            raise ValueError("Invalid query format: SQL-like queries not allowed")
        
        system_prompt = """
        You are a query parser that converts natural language queries about people into structured conditions.
        Output should be a list of tuples in the format: [("Person", "RELATION", "Object")]
        
        Valid relations are:
        - SPEAKS (for languages) - Use for: speaks, knows, can speak, is fluent in
        - WORKS_AT (for companies) - Use for: employed at, works for, is at
        - WORKS_IN (for industries) - Use for: works in, specializes in, focused on
        - LIVES_IN (for countries) - Use for: based in, located in, resides in
        - STUDIED_AT (for universities) - Use for: graduated from, attended, studied at
        
        Special cases:
        - Terms like "developer", "dev", "engineer" → ("Person", "WORKS_IN", "Software Development")
        - Company abbreviations: "MS" → "Microsoft"
        
        Examples:
        "Find developers"
        → [("Person", "WORKS_IN", "Software Development")]
        
        "Find people at MS"
        → [("Person", "WORKS_AT", "Microsoft")]
        
        "Find developers who speak English"
        → [("Person", "WORKS_IN", "Software Development"), ("Person", "SPEAKS", "English")]
        
        Important: Always return a valid Python list of tuples that can be evaluated with eval().
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query_text}
                ],
                temperature=0.1,
                timeout=30  # Add timeout
            )
            
            result_text = response.choices[0].message.content.strip()
            
            if result_text.startswith("ERROR:"):
                raise ValueError(result_text)
            
            # Clean and evaluate the string
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
                
                # Apply standardization with dynamic company normalization
                standardized_conditions = []
                for subject, relation, obj in conditions:
                    if relation == "WORKS_AT":
                        obj = self.normalize_company_name(obj)
                    if relation in standardization_rules:
                        obj = standardization_rules[relation](obj)
                    standardized_conditions.append((subject, relation, obj))
                
                return standardized_conditions
                
            except Exception as e:
                raise ValueError(f"Failed to parse GPT response into tuples: {str(e)}")
                
        except TimeoutError as e:
            raise ValueError(f"Request timed out: {str(e)}")
        except Exception as e:
            raise ValueError(f"Failed to parse query: {str(e)}") 