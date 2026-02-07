from pydantic import BaseModel, Field
from typing import List, Optional

class Author(BaseModel):
    name: str

class PaperSource(BaseModel):
    url: str
    label: str  # "Publisher Page", "Open Access PDF", "Repository Version", "Preprint"
    access_type: str # "oa", "paywalled", "repository", "preprint", "canonical"

class ScholarlyPaper(BaseModel):
    title: str
    authors: List[Author]
    year: Optional[int] = None
    journal: Optional[str] = None
    doi: Optional[str] = None
    sources: List[PaperSource] = []
    source_api: str # The API that first discovered this record
    citation_count: Optional[int] = 0
    relevance_score: Optional[float] = 0.0
    bibtex: Optional[str] = None
    ris: Optional[str] = None

class SearchResponse(BaseModel):
    results: List[ScholarlyPaper]
    total_found: int
    query: str
