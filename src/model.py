from typing import Callable
from pydantic import BaseModel


class Query(BaseModel):
    conditions: list[tuple[str, str, str]]

class QueryResult(BaseModel):
    query: Query
    matches: list[str]

QueryGraph = Callable[[Query], QueryResult]
