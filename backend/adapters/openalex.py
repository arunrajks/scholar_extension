from adapters.base import BaseAdapter
from models import ScholarlyPaper, Author, PaperSource, Researcher
from typing import List

class OpenAlexAdapter(BaseAdapter):
    async def search(self, query: str, limit: int = 10) -> List[ScholarlyPaper]:
        url = "https://api.openalex.org/works"
        params = {
            "search": query,
            "per_page": limit,
        }
        
        try:
            data = await self.fetch_json(url, params=params)
            items = data.get("results", [])
            
            results = []
            for item in items:
                authors = [Author(name=a.get("author", {}).get("display_name", "")) for a in item.get("authorships", [])]
                
                sources = []
                
                # Primary location
                primary = item.get("primary_location") or {}
                if primary.get("landing_page_url"):
                    sources.append(PaperSource(
                        url=primary["landing_page_url"],
                        label="Publisher Page",
                        access_type="oa" if item.get("open_access", {}).get("is_oa") else "paywalled"
                    ))
                
                # PDF links
                if primary.get("pdf_url"):
                    sources.append(PaperSource(
                        url=primary["pdf_url"],
                        label="Open Access PDF",
                        access_type="oa"
                    ))
                
                # Other locations (Repositories, etc.)
                for loc in item.get("locations", []):
                    if loc.get("landing_page_url") and loc.get("landing_page_url") not in [s.url for s in sources]:
                        is_oa = loc.get("is_oa")
                        sources.append(PaperSource(
                            url=loc["landing_page_url"],
                            label="Repository Version" if loc.get("location_type") == "repository" else "Publisher Page",
                            access_type="oa" if is_oa else "paywalled"
                        ))
                    if loc.get("pdf_url") and loc.get("pdf_url") not in [s.url for s in sources]:
                        sources.append(PaperSource(
                            url=loc["pdf_url"],
                            label="Open Access PDF",
                            access_type="oa"
                        ))

                results.append(ScholarlyPaper(
                    title=item.get("display_name", "Unknown Title"),
                    authors=authors,
                    year=item.get("publication_year"),
                    journal=item.get("primary_location", {}).get("source", {}).get("display_name", ""),
                    doi=item.get("doi", "").split("doi.org/")[-1] if item.get("doi") else None,
                    sources=sources,
                    source_api="OpenAlex",
                    citation_count=item.get("cited_by_count", 0),
                    relevance_score=item.get("relevance_score", 0)
                ))
            return results
        except Exception as e:
            print(f"OpenAlex Error: {e}")
            return []

    async def search_authors(self, query: str, limit: int = 10) -> List[Researcher]:
        url = "https://api.openalex.org/authors"
        params = {
            "search": query,
            "per_page": limit,
        }
        
        try:
            data = await self.fetch_json(url, params=params)
            items = data.get("results", [])
            
            results = []
            for item in items:
                results.append(Researcher(
                    name=item.get("display_name", "Unknown Researcher"),
                    id=item.get("id"),
                    affiliation=item.get("last_known_institution", {}).get("display_name"),
                    h_index=item.get("summary_stats", {}).get("h_index", 0),
                    citation_count=item.get("cited_by_count", 0),
                    paper_count=item.get("works_count", 0),
                    url=item.get("id"),
                    source="OpenAlex"
                ))
            return results
        except Exception as e:
            print(f"OpenAlex Author Error: {e}")
            return []
