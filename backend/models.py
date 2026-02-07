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
    formatted_citations: Dict[str, str] = {} # e.g. {"apa": "...", "nature": "..."}

class Researcher(BaseModel):
    name: str
    id: Optional[str] = None
    affiliation: Optional[str] = None
    h_index: Optional[int] = 0
    citation_count: Optional[int] = 0
    paper_count: Optional[int] = 0
    url: Optional[str] = None
    source: str

class AuthorSearchResponse(BaseModel):
    results: List[Researcher]
    total_found: int
    query: str

class SearchResponse(BaseModel):
    results: List[ScholarlyPaper]
    total_found: int
    query: str
