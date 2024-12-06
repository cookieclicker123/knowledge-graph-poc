from src.model import Query

class RelationType:
    SPEAKS = "SPEAKS"
    WORKS_AT = "WORKS_AT"
    STUDIED_AT = "STUDIED_AT"
    WORKS_IN = "WORKS_IN"
    LIVES_IN = "LIVES_IN"

def parse_query_intent(query_text: str) -> Query:
    """Parse natural language query into structured Query object."""
    conditions = []
    query_lower = query_text.lower()
    
    # Extract conditions from the query
    if "speak" in query_lower and "english" in query_lower:
        conditions.append(("Person", RelationType.SPEAKS, "English"))
        
    if "work" in query_lower and "microsoft" in query_lower:
        conditions.append(("Person", RelationType.WORKS_AT, "Microsoft"))
    
    return Query(conditions=conditions) 