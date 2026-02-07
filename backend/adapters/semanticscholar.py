from adapters.base import BaseAdapter
from models import ScholarlyPaper, Author, PaperSource
from typing import List

class SemanticScholarAdapter(BaseAdapter):
    async def search(self, query: str, limit: int = 10) -> List[ScholarlyPaper]:
        url = "https://api.semanticscholar.org/graph/v1/paper/search"
        params = {
            "query": query,
            "limit": limit,
            "fields": "title,authors,year,venue,externalIds,citationCount,openAccessPdf,url"
        }
        
        try:
            data = await self.fetch_json(url, params=params)
            items = data.get("data", [])
            
            results = []
            for item in items:
                authors = [Author(name=a.get("name", "")) for a in item.get("authors", [])]
                
                doi = item.get("externalIds", {}).get("DOI")
                sources = []
                
                # S2 URL
                if item.get("url"):
                    sources.append(PaperSource(
                        url=item["url"],
                        label="Semantic Scholar Page",
                        access_type="canonical"
                    ))
                
                # DOI Link
                if doi:
                    sources.append(PaperSource(
                        url=f"https://doi.org/{doi}",
                        label="Publisher Page",
                        access_type="paywalled"
                    ))
                
                # PDF Link
                if item.get("openAccessPdf") and item.get("openAccessPdf", {}).get("url"):
                    sources.append(PaperSource(
                        url=item["openAccessPdf"]["url"],
                        label="Open Access PDF",
                        access_type="oa"
                    ))
                
                results.append(ScholarlyPaper(
                    title=item.get("title", "Unknown Title"),
                    authors=authors,
                    year=item.get("year"),
                    journal=item.get("venue"),
                    doi=doi,
                    sources=sources,
                    source_api="Semantic Scholar",
                    citation_count=item.get("citationCount", 0)
                ))
            return results
        except Exception as e:
            print(f"Semantic Scholar Error: {e}")
            return []

    async def search_authors(self, query: str, limit: int = 10) -> List[Researcher]:
        url = "https://api.semanticscholar.org/graph/v1/author/search"
        params = {
            "query": query,
            "limit": limit,
            "fields": "name,affiliations,hIndex,citationCount,paperCount,url"
        }
        
        try:
            data = await self.fetch_json(url, params=params)
            items = data.get("data", [])
            
            from models import Researcher
            results = []
            for item in items:
                affiliations = item.get("affiliations", [])
                affiliation = affiliations[0] if affiliations else None
                
                results.append(Researcher(
                    name=item.get("name", "Unknown Researcher"),
                    id=item.get("authorId"),
                    affiliation=affiliation,
                    h_index=item.get("hIndex", 0),
                    citation_count=item.get("citationCount", 0),
                    paper_count=item.get("paperCount", 0),
                    url=item.get("url"),
                    source="Semantic Scholar"
                ))
            return results
        except Exception as e:
            print(f"Semantic Scholar Author Error: {e}")
            return []
