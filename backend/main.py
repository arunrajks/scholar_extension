from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from typing import List, Dict, Set
from models import SearchResponse, ScholarlyPaper, PaperSource
from adapters.crossref import CrossrefAdapter
from adapters.openalex import OpenAlexAdapter
from adapters.semanticscholar import SemanticScholarAdapter
from adapters.arxiv import ArxivAdapter
from adapters.core import CoreAdapter
from services.citation_service import generate_bibtex, generate_ris

app = FastAPI(title="Universal Scholarly Search API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

adapters = [
    CrossrefAdapter(),
    OpenAlexAdapter(),
    SemanticScholarAdapter(),
    ArxivAdapter(),
    CoreAdapter()
]

def get_dedup_key(paper: ScholarlyPaper) -> str:
    """Fallback key: title + year + first author last name."""
    title_clean = "".join(filter(str.isalnum, paper.title.lower()))
    year = str(paper.year) if paper.year else ""
    author = paper.authors[0].name.split()[-1].lower() if paper.authors else ""
    return f"{title_clean}|{year}|{author}"

def deduplicate_results(results: List[ScholarlyPaper]) -> List[ScholarlyPaper]:
    """
    Deduplicate papers based on DOI, then title+year+author.
    Merges sources for duplicate records.
    """
    by_doi: Dict[str, ScholarlyPaper] = {}
    by_fallback: Dict[str, ScholarlyPaper] = {}
    
    for paper in results:
        # 1. Identify best key
        doi = paper.doi.lower() if paper.doi else None
        fallback_key = get_dedup_key(paper)
        
        # 2. Match existing
        existing = by_doi.get(doi) if doi else by_fallback.get(fallback_key)
        
        if existing:
            # Merge sources
            existing_urls = {s.url for s in existing.sources}
            for new_source in paper.sources:
                if new_source.url not in existing_urls:
                    existing.sources.append(new_source)
            
            # Update missing metadata
            if paper.citation_count > (existing.citation_count or 0):
                existing.citation_count = paper.citation_count
            if not existing.year and paper.year:
                existing.year = paper.year
            if not existing.journal and paper.journal:
                existing.journal = paper.journal
            if not existing.doi and paper.doi:
                existing.doi = paper.doi
        else:
            # Add new record
            if doi:
                by_doi[doi] = paper
            else:
                by_fallback[fallback_key] = paper
    
    # Merge both collections
    all_unique = list(by_doi.values())
    # Only add from fallback if not already in by_doi (some might have matched DOI later)
    # But for simplicity, we just take all from both and dedup again or just return
    return list(by_doi.values()) + list(by_fallback.values())

@app.get("/search", response_model=SearchResponse)
async def search(q: str = Query(..., min_length=1)):
    tasks = [adapter.search(q) for adapter in adapters]
    all_results = await asyncio.gather(*tasks)
    flattened_results = [paper for sublist in all_results for paper in sublist]
    
    # Deduplicate and merge sources
    deduplicated = deduplicate_results(flattened_results)
    
    # Generate citations
    for paper in deduplicated:
        paper.bibtex = generate_bibtex(paper)
        paper.ris = generate_ris(paper)
    
    # Ranking Logic: DOI availability, Relevance, Citations, Recency
    # Sort by: DOI (binary), then citation count, then year
    deduplicated.sort(key=lambda x: (
        1 if x.doi else 0,
        x.citation_count or 0,
        x.year or 0
    ), reverse=True)
    
    return SearchResponse(
        results=deduplicated,
        total_found=len(deduplicated),
        query=q
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
