import os
from dotenv import load_dotenv
from openai import OpenAI
from typing import Dict, Set, Optional, Any
import re
import pandas as pd
from itertools import chain

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
            
            # Base language mappings (static)
            self.base_language_mappings = {
                'inglês': 'English',
                'anglais': 'English',
                'français': 'French',
                'francés': 'French',
                'español': 'Spanish',
                'inglés': 'English',
                'portuguese': 'Portuguese',
                'italiano': 'Italian',
                'japanese': 'Japanese'
            }
            
            # Dynamic language mappings from CSV
            self.language_mappings = self._build_language_mappings(data_path)
            self.university_mappings = self._build_university_mappings(data_path)
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

    def _build_university_mappings(self, data_path: str) -> Dict[str, str]:
        """Build mappings for university name variations"""
        mappings = {}
        try:
            df = pd.read_csv(data_path)
            universities = set(df['university'].dropna().unique())
            
            for uni in universities:
                # Full name
                mappings[uni.lower()] = uni
                
                # Common abbreviations
                if "University of California" in uni:
                    mappings['ucla'] = uni
                    mappings['uc los angeles'] = uni
                
                # Remove "University" suffix/prefix
                base_name = re.sub(r'\s+(?:University|College|Institute|School).*$', '', uni)
                if base_name != uni:
                    mappings[base_name.lower()] = uni
            
            return mappings
            
        except Exception as e:
            raise ValueError(f"Failed to build university mappings: {str(e)}")

    def _build_language_mappings(self, data_path: str) -> Dict[str, str]:
        """Build comprehensive language mappings from CSV data and base mappings"""
        try:
            df = pd.read_csv(data_path)
            
            # Get all unique languages from the CSV
            all_languages = set(chain.from_iterable(
                lang.split('|') for lang in df['languages'].dropna()
            ))
            
            mappings = {}
            
            # Add base mappings
            mappings.update(self.base_language_mappings)
            
            # Add reverse mappings
            reverse_mappings = {v.lower(): k for k, v in self.base_language_mappings.items()}
            mappings.update(reverse_mappings)
            
            # Add CSV languages and their variations
            for lang in all_languages:
                lang_lower = lang.lower()
                # Map each language to itself and its known variations
                mappings[lang_lower] = lang
                # Add common variations
                if lang_lower in ['english', 'inglês', 'anglais']:
                    for variant in ['english', 'inglês', 'anglais']:
                        mappings[variant] = lang
                elif lang_lower in ['spanish', 'español', 'espanol']:
                    for variant in ['spanish', 'español', 'espanol']:
                        mappings[variant] = lang
                elif lang_lower in ['french', 'français', 'francés']:
                    for variant in ['french', 'français', 'francés']:
                        mappings[variant] = lang
                elif lang_lower in ['portuguese', 'português', 'portugues']:
                    for variant in ['portuguese', 'português', 'portugues']:
                        mappings[variant] = lang
            
            return mappings
            
        except Exception as e:
            raise ValueError(f"Failed to build language mappings: {str(e)}")

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

    def normalize_language(self, language: str) -> str:
        """Normalize language names using comprehensive mappings"""
        if not language:
            return language
        
        language_lower = language.lower().strip()
        
        # Special handling for English variations
        if language_lower in ['english', 'inglês', 'anglais', 'ingles']:
            return 'Inglês'  # Match exactly what's in our CSV
        
        # Special handling for French variations
        if language_lower in ['french', 'français', 'francés']:
            return 'French'  # Standardize to English name for French
        
        # Direct lookup in mappings
        if language_lower in self.language_mappings:
            return self.language_mappings[language_lower]
        
        # Try partial matches
        for known_lang, canonical_form in self.language_mappings.items():
            if known_lang in language_lower or language_lower in known_lang:
                return canonical_form
        
        # If no match found, return the original with title case
        return language.title()

    def normalize_university(self, university: str) -> str:
        """Find the best matching university name"""
        university_lower = university.lower()
        
        # Direct match
        if university_lower in self.university_mappings:
            return self.university_mappings[university_lower]
        
        # Partial match
        for known_name, canonical_name in self.university_mappings.items():
            if known_name in university_lower or university_lower in known_name:
                return canonical_name
        
        return university.title()

    def parse_query(self, query_text: Any) -> list[tuple[str, str, str]]:
        """Parse natural language query into structured conditions"""
        # Validate input type and content
        if not isinstance(query_text, str):
            raise ValueError("Invalid query format: input must be a string")
        
        query_text = str(query_text).strip()
        if not query_text:
            raise ValueError("Invalid query format: query cannot be empty")
        
        # Check for SQL injection attempts
        if any(keyword in query_text.lower() for keyword in ['select', 'insert', 'update', 'delete', 'drop']):
            raise ValueError("Invalid query format: SQL-like queries not allowed")
        
        # Check for unsupported query types
        if any(phrase in query_text.lower() for phrase in ['average', 'count', 'how many']):
            raise ValueError("Invalid query format: unsupported query type")
        
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
                timeout=30
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
                
                # Apply standardization one relation at a time
                standardized_conditions = []
                for subject, relation, obj in conditions:
                    standardized_obj = obj  # Default to original value
                    
                    if relation == "SPEAKS":
                        standardized_obj = self.normalize_language(obj)
                    elif relation == "WORKS_AT":
                        standardized_obj = self.normalize_company_name(obj)
                    elif relation == "STUDIED_AT":
                        standardized_obj = self.normalize_university(obj)
                    elif relation == "WORKS_IN":
                        standardized_obj = obj.title()
                    elif relation == "LIVES_IN":
                        standardized_obj = obj.title()
                    
                    standardized_conditions.append((subject, relation, standardized_obj))
                
                return standardized_conditions
                
            except Exception as e:
                raise ValueError(f"Failed to parse GPT response into tuples: {str(e)}")
                
        except TimeoutError as e:
            raise ValueError(f"Request timed out: {str(e)}")
        except Exception as e:
            raise ValueError(f"Failed to parse query: {str(e)}")

    def get_completion(self, prompt: str) -> str:
        """Get a direct completion from GPT"""
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("Prompt must be a non-empty string")
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        return response.choices[0].message.content 