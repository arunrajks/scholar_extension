from adapters.base import BaseAdapter
from models import ScholarlyPaper, Author, PaperSource
from typing import List

class CrossrefAdapter(BaseAdapter):
    async def search(self, query: str, limit: int = 10) -> List[ScholarlyPaper]:
        url = "https://api.crossref.org/works"
        params = {
            "query": query,
            "rows": limit,
            "select": "DOI,title,author,issued,container-title,is-referenced-by-count,URL"
        }
        
        try:
            data = await self.fetch_json(url, params=params)
            items = data.get("message", {}).get("items", [])
            
            results = []
            for item in items:
                title = item.get("title", ["Unknown Title"])[0]
                doi = item.get("DOI")
                url_link = item.get("URL", f"https://doi.org/{doi}" if doi else "")
                
                authors = []
                for a in item.get("author", []):
                    name = f"{a.get('given', '')} {a.get('family', '')}".strip()
                    if name:
                        authors.append(Author(name=name))
                
                year = None
                issued = item.get("issued", {}).get("date-parts", [])
                if issued and issued[0]:
                    year = issued[0][0]
                
                sources = []
                if url_link:
                    sources.append(PaperSource(
                        url=url_link,
                        label="Publisher Page",
                        access_type="paywalled" # Default for Crossref/Publisher
                    ))

                results.append(ScholarlyPaper(
                    title=title,
                    authors=authors,
                    year=year,
                    journal=item.get("container-title", [""])[0],
                    doi=doi,
                    sources=sources,
                    source_api="Crossref",
                    citation_count=item.get("is-referenced-by-count", 0)
                ))
            return results
        except Exception as e:
            print(f"Crossref Error: {e}")
            return []
